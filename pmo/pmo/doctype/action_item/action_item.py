# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from pmo.pmo import assignments


class ActionItem(Document):
	def validate(self):
		self.set_completed_on()
		self.validate_parent_action_item()

	def on_update(self):
		assignments.sync_coordinator(self)

	def set_completed_on(self):
		if self.status != "Completed":
			self.completed_on = None
		elif not self.completed_on:
			self.completed_on = today()

	def validate_parent_action_item(self):
		if not self.parent_action_item:
			return

		seen = {self.name}
		ancestor = self.parent_action_item

		while ancestor:
			if ancestor in seen:
				frappe.throw(
					_("Action Item {0} cannot be its own ancestor").format(self.name),
					frappe.CircularLinkingError,
				)
			seen.add(ancestor)
			ancestor = frappe.db.get_value("Action Item", ancestor, "parent_action_item")
