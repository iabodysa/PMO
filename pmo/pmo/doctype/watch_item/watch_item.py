# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, cint, getdate

from pmo.pmo.assignments import sync_coordinator

FREQUENCY_DAYS = {"Weekly": 7, "Biweekly": 14}


class WatchItem(Document):
	def validate(self):
		self.validate_update_frequency()
		self.set_next_update_due()

	def on_update(self):
		sync_coordinator(self)

	def validate_update_frequency(self):
		if self.update_frequency != "Custom":
			self.custom_frequency_days = None
			return

		if not self.custom_frequency_days:
			frappe.throw(_("Custom Frequency Days is required when Update Frequency is Custom"))

	def set_next_update_due(self):
		if not self.update_frequency:
			self.next_update_due = None
			return

		if self.next_update_due and not (
			self.has_value_changed("update_frequency") or self.has_value_changed("custom_frequency_days")
		):
			return

		self.next_update_due = calculate_next_update_due(self)


def last_update_date(doc, exclude=None):
	from pmo.pmo.doctype.progress_update.progress_update import newest_progress_update

	newest = newest_progress_update("Watch Item", doc.name, exclude)
	return newest.update_date if newest else doc.get("creation")


def calculate_next_update_due(watch_item, from_date=None):
	doc = frappe.get_doc("Watch Item", watch_item) if isinstance(watch_item, str) else watch_item

	if from_date is None:
		from_date = last_update_date(doc)

	base = getdate(from_date)
	frequency = doc.get("update_frequency")

	if frequency == "Custom":
		days = cint(doc.get("custom_frequency_days"))
		return add_days(base, days) if days > 0 else None

	if frequency == "Monthly":
		return add_months(base, 1)

	days = FREQUENCY_DAYS.get(frequency)
	return add_days(base, days) if days else None


def refresh_next_update_due(watch_item, exclude=None):
	doc = frappe.get_doc("Watch Item", watch_item)
	due = calculate_next_update_due(doc, from_date=last_update_date(doc, exclude))

	current = getdate(doc.next_update_due) if doc.next_update_due else None
	if current != due:
		frappe.db.set_value("Watch Item", doc.name, "next_update_due", due, update_modified=False)

	return due
