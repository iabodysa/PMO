# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, today

OVERDUE_NUMBER_CARD = "Overdue Action Items"
STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]


def new_owner_unit(unit_name):
	return frappe.get_doc({"doctype": "Unit", "unit_name": unit_name}).insert().name


def new_action_item(subject, owner_unit, due_date=None, status="In Progress"):
	return frappe.get_doc(
		{
			"doctype": "Action Item",
			"subject": subject,
			"owner_unit": owner_unit,
			"due_date": due_date,
			"status": status,
		}
	).insert()


class TestActionItem(IntegrationTestCase):
	def make_coordinator(self):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": f"{frappe.generate_hash(length=10)}@pmo.test",
				"first_name": "PMO Coordinator",
				"send_welcome_email": 0,
				"roles": [{"role": "PMO Manager"}],
			}
		).insert()
		return user.name

	def make_action_item(self, coordinator):
		unit = frappe.get_doc(
			{
				"doctype": "Unit",
				"unit_name": f"Test Unit {frappe.generate_hash(length=8)}",
				"unit_type": "Department",
			}
		).insert()
		return frappe.get_doc(
			{
				"doctype": "Action Item",
				"subject": f"Test Action Item {frappe.generate_hash(length=8)}",
				"owner_unit": unit.name,
				"pmo_coordinator": coordinator,
			}
		).insert()

	def assignees(self, item, status):
		return set(
			frappe.get_all(
				"ToDo",
				filters={
					"reference_type": "Action Item",
					"reference_name": item.name,
					"status": status,
				},
				pluck="allocated_to",
			)
		)

	def test_setting_a_pmo_coordinator_opens_a_native_todo_for_that_user(self):
		coordinator = self.make_coordinator()

		item = self.make_action_item(coordinator)

		self.assertEqual(self.assignees(item, "Open"), {coordinator})

	def test_changing_the_pmo_coordinator_moves_the_open_todo_to_the_new_user(self):
		previous = self.make_coordinator()
		current = self.make_coordinator()
		item = self.make_action_item(previous)

		item.pmo_coordinator = current
		item.save()

		self.assertEqual(self.assignees(item, "Open"), {current})
		self.assertEqual(self.assignees(item, "Cancelled"), {previous})

	def test_resaving_with_the_same_pmo_coordinator_leaves_exactly_one_open_todo(self):
		coordinator = self.make_coordinator()
		item = self.make_action_item(coordinator)

		item.subject = f"{item.subject} rewritten"
		item.save()

		self.assertEqual(
			frappe.db.count(
				"ToDo",
				{
					"reference_type": "Action Item",
					"reference_name": item.name,
					"status": "Open",
					"allocated_to": coordinator,
				},
			),
			1,
		)


class TestActionItemCompletionTimestamp(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		self.action_item = new_action_item(
			"Completion timestamp subject", new_owner_unit("Completion Timestamp Unit")
		)

	def stored_completed_on(self):
		return frappe.db.get_value("Action Item", self.action_item.name, "completed_on")

	def test_completed_on_is_stamped_with_today_when_the_status_becomes_completed(self):
		self.assertIsNone(self.stored_completed_on())

		self.action_item.status = "Completed"
		self.action_item.save()

		self.assertEqual(self.stored_completed_on(), getdate(today()))

	def test_a_completed_on_already_stamped_survives_a_save_that_leaves_the_status_completed(self):
		earlier = add_days(today(), -7)
		self.action_item.status = "Completed"
		self.action_item.save()
		frappe.db.set_value("Action Item", self.action_item.name, "completed_on", earlier)
		self.action_item.reload()

		self.action_item.subject = "Completion timestamp subject rewritten"
		self.action_item.save()

		self.assertEqual(self.stored_completed_on(), getdate(earlier))

	def test_completed_on_is_cleared_when_a_completed_action_item_is_reopened(self):
		self.action_item.status = "Completed"
		self.action_item.save()
		self.assertEqual(self.stored_completed_on(), getdate(today()))

		self.action_item.status = "In Progress"
		self.action_item.save()

		self.assertIsNone(self.stored_completed_on())


class TestActionItemOverdueCalculation(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.owner_unit = new_owner_unit("Overdue Calculation Unit")
		past_due = add_days(today(), -3)
		cls.past_due_and_open = new_action_item("Past due and still open", cls.owner_unit, past_due).name
		new_action_item("Past due but completed", cls.owner_unit, past_due, status="Completed")
		new_action_item("Due today and still open", cls.owner_unit, today())
		new_action_item("Open with no due date at all", cls.owner_unit)

	def test_overdue_is_never_offered_as_a_stored_action_item_status(self):
		options = frappe.get_meta("Action Item").get_field("status").options.split("\n")

		self.assertEqual(options, STATUS_OPTIONS)

	def test_the_shipped_number_card_reads_overdue_as_due_date_before_today_and_status_not_completed(self):
		card = frappe.get_doc("Number Card", OVERDUE_NUMBER_CARD)

		self.assertEqual(card.document_type, "Action Item")
		self.assertEqual(
			json.loads(card.filters_json),
			[
				["Action Item", "status", "!=", "Completed"],
				["Action Item", "due_date", "is", "set"],
			],
		)
		self.assertEqual(
			json.loads(card.dynamic_filters_json),
			[["Action Item", "due_date", "<", "frappe.datetime.get_today()"]],
		)

	def test_the_overdue_formula_takes_only_the_past_due_item_that_is_not_completed(self):
		population = frappe.get_all("Action Item", filters={"owner_unit": self.owner_unit}, pluck="name")
		overdue = frappe.get_all(
			"Action Item",
			filters=[
				["owner_unit", "=", self.owner_unit],
				["status", "!=", "Completed"],
				["due_date", "is", "set"],
				["due_date", "<", today()],
			],
			pluck="name",
		)

		self.assertEqual(len(population), 4)
		self.assertEqual(overdue, [self.past_due_and_open])
