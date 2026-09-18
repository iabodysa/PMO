# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class Submission(Document):
	def validate(self):
		self.validate_one_submission_per_cycle_and_unit()
		self.set_submitted_on()

	def validate_one_submission_per_cycle_and_unit(self):
		if not (self.submission_cycle and self.unit):
			return

		existing = frappe.db.exists(
			"Submission",
			{
				"submission_cycle": self.submission_cycle,
				"unit": self.unit,
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				_("{0} already holds submission {1} for unit {2}").format(
					self.submission_cycle, existing, self.unit
				)
			)

	def set_submitted_on(self):
		if self.status == "Draft":
			self.submitted_on = None
		elif not self.submitted_on:
			self.submitted_on = now_datetime()


def on_doctype_update():
	frappe.db.add_unique("Submission", ["submission_cycle", "unit"], constraint_name="unique_cycle_unit")
