# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import getdate

OLDER_DATE = "2026-01-05"
NEWER_DATE = "2026-03-10"
OLDER_TEXT = "January update"
NEWER_TEXT = "March update"


class TestProgressUpdate(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		unit = frappe.get_doc({"doctype": "Unit", "unit_name": "Progress Update Test Unit"}).insert()
		self.action_item = frappe.get_doc(
			{
				"doctype": "Action Item",
				"subject": "Progress Update synchronization subject",
				"owner_unit": unit.name,
			}
		).insert()

	def add_progress_update(self, update_date, update_text):
		return frappe.get_doc(
			{
				"doctype": "Progress Update",
				"reference_doctype": "Action Item",
				"reference_name": self.action_item.name,
				"update_date": update_date,
				"update_source": "PMO",
				"update_text": update_text,
			}
		).insert()

	def stored_latest(self):
		return frappe.db.get_value(
			"Action Item",
			self.action_item.name,
			["latest_update", "latest_update_on"],
			as_dict=True,
		)

	def test_latest_update_is_taken_from_the_newest_update_date_not_the_last_inserted_record(self):
		self.add_progress_update(NEWER_DATE, NEWER_TEXT)
		self.add_progress_update(OLDER_DATE, OLDER_TEXT)

		latest = self.stored_latest()
		self.assertEqual(latest.latest_update, NEWER_TEXT)
		self.assertEqual(latest.latest_update_on, getdate(NEWER_DATE))

	def test_editing_an_older_progress_update_leaves_the_newest_one_as_the_latest_update(self):
		self.add_progress_update(NEWER_DATE, NEWER_TEXT)
		older = self.add_progress_update(OLDER_DATE, OLDER_TEXT)

		older.update_text = "January update rewritten"
		older.save()

		latest = self.stored_latest()
		self.assertEqual(latest.latest_update, NEWER_TEXT)
		self.assertEqual(latest.latest_update_on, getdate(NEWER_DATE))

	def test_deleting_the_newest_progress_update_restores_the_previous_one_as_the_latest_update(self):
		self.add_progress_update(OLDER_DATE, OLDER_TEXT)
		newest = self.add_progress_update(NEWER_DATE, NEWER_TEXT)

		newest.delete()

		latest = self.stored_latest()
		self.assertEqual(latest.latest_update, OLDER_TEXT)
		self.assertEqual(latest.latest_update_on, getdate(OLDER_DATE))
