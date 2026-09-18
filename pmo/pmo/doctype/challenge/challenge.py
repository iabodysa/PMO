# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from pmo.services import assignments

RESOLVED_STATUSES = ("Resolved", "Closed")


class Challenge(Document):
	def validate(self):
		self.set_resolved_on()
		self.set_escalated_on()
		self.validate_date_order()

	def on_update(self):
		assignments.sync_coordinator(self)

	def set_resolved_on(self):
		if self.status in RESOLVED_STATUSES:
			if not self.resolved_on:
				self.resolved_on = nowdate()
		else:
			self.resolved_on = None

	def set_escalated_on(self):
		if self.is_escalated:
			if not self.escalated_on:
				self.escalated_on = nowdate()
		else:
			self.escalated_on = None

	def validate_date_order(self):
		if not self.opened_on:
			return

		opened_on = getdate(self.opened_on)

		if self.resolved_on and getdate(self.resolved_on) < opened_on:
			frappe.throw(_("Resolved On cannot be earlier than Opened On"))

		if self.escalated_on and getdate(self.escalated_on) < opened_on:
			frappe.throw(_("Escalated On cannot be earlier than Opened On"))
