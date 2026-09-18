# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

from frappe.desk.form.assign_to import _add, _remove, close_all_assignments

TERMINAL_STATUSES = {
	"Action Item": ("Completed",),
	"Challenge": ("Resolved", "Closed"),
	"Watch Item": ("Closed",),
}


def previous_value(doc, fieldname):
	before = doc.get_doc_before_save()
	return before.get(fieldname) if before else None


def sync_coordinator(doc):
	terminal = TERMINAL_STATUSES.get(doc.doctype, ())
	status_changed = doc.has_value_changed("status")

	if doc.get("status") in terminal:
		if status_changed:
			close_all_assignments(doc.doctype, doc.name, ignore_permissions=True)
		return

	reopened = status_changed and previous_value(doc, "status") in terminal
	if not (doc.has_value_changed("pmo_coordinator") or reopened):
		return

	previous_coordinator = previous_value(doc, "pmo_coordinator")
	if previous_coordinator and previous_coordinator != doc.pmo_coordinator:
		_remove(doc.doctype, doc.name, previous_coordinator, ignore_permissions=True)

	if not doc.pmo_coordinator:
		return

	args = {
		"assign_to": [doc.pmo_coordinator],
		"doctype": doc.doctype,
		"name": doc.name,
		"description": doc.get("subject") or doc.get("title"),
	}
	if doc.get("priority"):
		args["priority"] = doc.priority
	if doc.get("due_date"):
		args["date"] = doc.due_date

	_add(args, ignore_permissions=True)
