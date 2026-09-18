# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from pmo.services.assignments import sync_coordinator
from pmo.services.progress import calculate_next_update_due


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
