# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import getdate

from pmo import hooks, tasks
from pmo.pmo.doctype.watch_item.watch_item import refresh_next_update_due

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

	def test_the_daily_scheduler_hook_names_a_task_that_resolves_to_a_callable(self):
		self.assertEqual(hooks.scheduler_events["daily"], ["pmo.tasks.reconcile_next_update_due"])
		self.assertTrue(callable(frappe.get_attr("pmo.tasks.reconcile_next_update_due")))

	def test_the_daily_scheduler_task_reconciles_through_the_watch_item_owned_helper(self):
		self.assertIs(tasks.refresh_next_update_due, refresh_next_update_due)
		self.assertEqual(refresh_next_update_due.__module__, "pmo.pmo.doctype.watch_item.watch_item")

	def test_the_daily_scheduler_task_restores_a_next_update_due_that_drifted(self):
		watch_item = self.watch_item("Weekly")
		self.add_progress_update(watch_item)
		frappe.db.set_value("Watch Item", watch_item.name, "next_update_due", "2000-01-01")

		tasks.reconcile_next_update_due()

		self.assertEqual(
			frappe.db.get_value("Watch Item", watch_item.name, "next_update_due"), getdate("2026-01-22")
		)
