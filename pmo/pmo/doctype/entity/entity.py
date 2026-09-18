# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Entity(Document):
	def validate(self):
		if self.entity_scope == "Internal" and not self.unit:
			frappe.throw(
				_("Unit is mandatory when Entity Scope is Internal"),
				frappe.MandatoryError,
			)
