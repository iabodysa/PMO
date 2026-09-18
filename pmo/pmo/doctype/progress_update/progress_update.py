# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from pmo.pmo.doctype.watch_item.watch_item import refresh_next_update_due

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


def newest_progress_update(reference_doctype, reference_name, exclude=None):
	filters = {"reference_doctype": reference_doctype, "reference_name": reference_name}
	if exclude:
		filters["name"] = ("!=", exclude)

	rows = frappe.get_all(
		"Progress Update",
		filters=filters,
		fields=["name", "update_text", "update_date"],
		order_by="update_date desc, creation desc",
		limit=1,
	)
	return rows[0] if rows else None


def refresh_latest_update(reference_doctype, reference_name, exclude=None):
	newest = newest_progress_update(reference_doctype, reference_name, exclude)
	frappe.db.set_value(
		reference_doctype,
		reference_name,
		{
			"latest_update": newest.update_text if newest else None,
			"latest_update_on": newest.update_date if newest else None,
		},
		update_modified=False,
	)

	if reference_doctype == "Watch Item":
		refresh_next_update_due(reference_name, exclude=exclude)

	return newest
