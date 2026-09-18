# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


class TestSubmission(IntegrationTestCase):
	def make_unit(self):
		return frappe.get_doc(
			{
				"doctype": "Unit",
				"unit_name": f"Test Unit {frappe.generate_hash(length=8)}",
				"unit_type": "Region",
			}
		).insert()

	def make_cycle(self):
		return frappe.get_doc(
			{
				"doctype": "Submission Cycle",
				"title": f"Test Cycle {frappe.generate_hash(length=8)}",
				"submission_type": "Challenges",
				"period_from": "2026-09-13",
				"period_to": "2026-09-17",
				"due_date": "2026-09-20",
			}
		).insert()

	def make_submission(self, cycle, unit):
		return frappe.get_doc(
			{"doctype": "Submission", "submission_cycle": cycle.name, "unit": unit.name}
		).insert()

	def test_a_second_submission_for_the_same_cycle_and_unit_is_rejected(self):
		cycle = self.make_cycle()
		unit = self.make_unit()
		self.make_submission(cycle, unit)

		with self.assertRaises(frappe.ValidationError):
			self.make_submission(cycle, unit)

	def test_one_unit_submits_to_two_cycles_without_collision(self):
		unit = self.make_unit()

		first = self.make_submission(self.make_cycle(), unit)
		second = self.make_submission(self.make_cycle(), unit)

		self.assertNotEqual(first.name, second.name)

	def test_resaving_a_submission_does_not_collide_with_itself(self):
		submission = self.make_submission(self.make_cycle(), self.make_unit())

		submission.status = "Submitted"
		submission.save()

		self.assertEqual(submission.status, "Submitted")
