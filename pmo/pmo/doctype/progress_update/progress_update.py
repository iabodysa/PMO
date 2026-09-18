# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from pmo.services.progress import refresh_latest_update

REFERENCE_DOCTYPES = ("Action Item", "Challenge", "Watch Item")


class ProgressUpdate(Document):
	def validate(self):
		if self.reference_doctype and self.reference_doctype not in REFERENCE_DOCTYPES:
			frappe.throw(
				_("A Progress Update may only refer to {0}.").format(", ".join(REFERENCE_DOCTYPES)),
				title=_("Reference Document Type Not Allowed"),
			)

	def after_insert(self):
		refresh_latest_update(self.reference_doctype, self.reference_name)

	def on_update(self):
		previous = self.get_doc_before_save()
		if previous and (previous.reference_doctype, previous.reference_name) != (
			self.reference_doctype,
			self.reference_name,
		):
			refresh_latest_update(previous.reference_doctype, previous.reference_name)

		refresh_latest_update(self.reference_doctype, self.reference_name)

	def on_trash(self):
		refresh_latest_update(self.reference_doctype, self.reference_name, exclude=self.name)
