# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, add_months, cint, getdate

FREQUENCY_DAYS = {"Weekly": 7, "Biweekly": 14}


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


def calculate_next_update_due(watch_item, from_date=None):
	doc = frappe.get_doc("Watch Item", watch_item) if isinstance(watch_item, str) else watch_item

	if from_date is None:
		newest = newest_progress_update("Watch Item", doc.name)
		from_date = newest.update_date if newest else doc.get("creation")

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
	newest = newest_progress_update("Watch Item", doc.name, exclude)
	due = calculate_next_update_due(doc, from_date=newest.update_date if newest else doc.creation)

	current = getdate(doc.next_update_due) if doc.next_update_due else None
	if current != due:
		frappe.db.set_value("Watch Item", doc.name, "next_update_due", due, update_modified=False)

	return due
