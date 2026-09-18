# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import getdate

UPDATE_DATE = "2026-01-15"
CUSTOM_DAYS = 10


class TestWatchItem(IntegrationTestCase):
	def watch_item(self, update_frequency, custom_frequency_days=None):
		return frappe.get_doc(
			{
				"doctype": "Watch Item",
				"title": f"Watch Item on a {update_frequency} frequency",
				"update_frequency": update_frequency,
				"custom_frequency_days": custom_frequency_days,
			}
		).insert()

	def add_progress_update(self, watch_item):
		frappe.get_doc(
			{
				"doctype": "Progress Update",
				"reference_doctype": "Watch Item",
				"reference_name": watch_item.name,
				"update_date": UPDATE_DATE,
				"update_source": "PMO",
				"update_text": "Watch Item progress",
			}
		).insert()

	def next_update_due_after_an_update(self, update_frequency, custom_frequency_days=None):
		watch_item = self.watch_item(update_frequency, custom_frequency_days)
		self.add_progress_update(watch_item)
		return frappe.db.get_value("Watch Item", watch_item.name, "next_update_due")

	def test_weekly_watch_item_falls_due_seven_days_after_its_newest_progress_update(self):
		self.assertEqual(self.next_update_due_after_an_update("Weekly"), getdate("2026-01-22"))

	def test_biweekly_watch_item_falls_due_fourteen_days_after_its_newest_progress_update(self):
		self.assertEqual(self.next_update_due_after_an_update("Biweekly"), getdate("2026-01-29"))

	def test_monthly_watch_item_falls_due_one_calendar_month_after_its_newest_progress_update(self):
		self.assertEqual(self.next_update_due_after_an_update("Monthly"), getdate("2026-02-15"))

	def test_custom_watch_item_falls_due_custom_frequency_days_after_its_newest_progress_update(self):
		self.assertEqual(self.next_update_due_after_an_update("Custom", CUSTOM_DAYS), getdate("2026-01-25"))
