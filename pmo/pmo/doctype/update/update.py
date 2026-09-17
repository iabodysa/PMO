# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Update(Document):
	def on_update(self):
		frappe.db.set_value(
			self.reference_doctype,
			self.reference_name,
			{"latest_update": self.update_text, "latest_update_on": self.update_date},
			update_modified=False,
		)

	def on_trash(self):
		latest = frappe.get_all(
			"Update",
			filters={
				"reference_doctype": self.reference_doctype,
				"reference_name": self.reference_name,
				"name": ("!=", self.name),
			},
			fields=["update_text", "update_date"],
			order_by="update_date desc, creation desc",
			limit=1,
		)
		frappe.db.set_value(
			self.reference_doctype,
			self.reference_name,
			{
				"latest_update": latest[0].update_text if latest else None,
				"latest_update_on": latest[0].update_date if latest else None,
			},
			update_modified=False,
		)
