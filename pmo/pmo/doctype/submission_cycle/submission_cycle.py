# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

SUBMITTED_STATUSES = ("Submitted", "Reviewed")


class SubmissionCycle(Document):
	def validate(self):
		self.validate_period()
		self.validate_due_date()

	def validate_period(self):
		if not (self.period_from and self.period_to):
			return

		if getdate(self.period_from) > getdate(self.period_to):
			frappe.throw(_("Period From must fall on or before Period To"))

	def validate_due_date(self):
		if not (self.due_date and self.period_from):
			return

		if getdate(self.due_date) < getdate(self.period_from):
			frappe.throw(_("Due Date must fall on or after Period From"))

	def on_update(self):
		driving_fields = ("period_from", "period_to", "due_date")
		if not any(self.has_value_changed(field) for field in driving_fields):
			return

		submissions = frappe.get_all("Submission", filters={"submission_cycle": self.name}, pluck="name")
		for name in submissions:
			frappe.get_doc("Submission", name).save(ignore_permissions=True)


def active_regions():
	return frappe.get_all("Unit", filters={"unit_type": "Region", "is_active": 1}, pluck="name")


@frappe.whitelist()
def generate_region_submissions(submission_cycle: str):
	frappe.get_doc("Submission Cycle", submission_cycle).check_permission("write")

	covered = set(
		frappe.get_all("Submission", filters={"submission_cycle": submission_cycle}, pluck="unit")
	)

	created = []
	for region in active_regions():
		if region in covered:
			continue

		submission = frappe.get_doc(
			{"doctype": "Submission", "submission_cycle": submission_cycle, "unit": region}
		).insert()
		created.append(submission.name)

	return created


@frappe.whitelist()
def get_cycle_statistics(submission_cycle: str):
	frappe.get_doc("Submission Cycle", submission_cycle).check_permission("read")

	total = len(active_regions())
	submitted = frappe.db.count(
		"Submission", {"submission_cycle": submission_cycle, "status": ("in", SUBMITTED_STATUSES)}
	)
	return {"total_regions": total, "submitted": submitted, "pending": max(total - submitted, 0)}
