# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe

SUBMITTED_STATUSES = ("Submitted", "Reviewed")


def active_regions():
	return frappe.get_all("Unit", filters={"unit_type": "Region", "is_active": 1}, pluck="name")


def generate_region_submissions(cycle):
	name = cycle if isinstance(cycle, str) else cycle.name
	covered = set(frappe.get_all("Submission", filters={"submission_cycle": name}, pluck="unit"))

	created = []
	for region in active_regions():
		if region in covered:
			continue

		submission = frappe.get_doc(
			{"doctype": "Submission", "submission_cycle": name, "unit": region}
		).insert()
		created.append(submission.name)

	return created


def get_cycle_statistics(cycle):
	name = cycle if isinstance(cycle, str) else cycle.name
	total = len(active_regions())
	submitted = frappe.db.count(
		"Submission", {"submission_cycle": name, "status": ("in", SUBMITTED_STATUSES)}
	)
	return {"total_regions": total, "submitted": submitted, "pending": max(total - submitted, 0)}
