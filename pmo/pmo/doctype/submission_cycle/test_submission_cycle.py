# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from pmo.pmo.doctype.submission_cycle.submission_cycle import generate_region_submissions
from pmo.services.submissions import active_regions


class TestSubmissionCycle(IntegrationTestCase):
	def make_unit(self, unit_type, is_active=1):
		return frappe.get_doc(
			{
				"doctype": "Unit",
				"unit_name": f"Test Unit {frappe.generate_hash(length=8)}",
				"unit_type": unit_type,
				"is_active": is_active,
			}
		).insert()

	def make_cycle(self):
		return frappe.get_doc(
			{
				"doctype": "Submission Cycle",
				"title": f"Test Cycle {frappe.generate_hash(length=8)}",
				"submission_type": "Challenges",
				"period_from": "2026-09-13",
				"period_to": "2026-09-17",
				"due_date": "2026-09-20",
			}
		).insert()

	def covered_units(self, cycle):
		return set(frappe.get_all("Submission", filters={"submission_cycle": cycle.name}, pluck="unit"))

	def test_generation_covers_every_active_region_and_no_other_unit(self):
		region = self.make_unit("Region")
		inactive_region = self.make_unit("Region", is_active=0)
		department = self.make_unit("Department")
		cycle = self.make_cycle()

		generate_region_submissions(cycle.name)

		covered = self.covered_units(cycle)
		self.assertIn(region.name, covered)
		self.assertNotIn(inactive_region.name, covered)
		self.assertNotIn(department.name, covered)
		self.assertEqual(covered, set(active_regions()))

	def test_regeneration_creates_no_duplicate_and_covers_only_a_region_added_since(self):
		self.make_unit("Region")
		cycle = self.make_cycle()
		first = generate_region_submissions(cycle.name)
		self.assertTrue(first)

		self.assertEqual(generate_region_submissions(cycle.name), [])
		self.assertEqual(frappe.db.count("Submission", {"submission_cycle": cycle.name}), len(first))

		late_region = self.make_unit("Region")
		third = generate_region_submissions(cycle.name)

		self.assertEqual(
			[frappe.db.get_value("Submission", name, "unit") for name in third], [late_region.name]
		)
		self.assertEqual(frappe.db.count("Submission", {"submission_cycle": cycle.name}), len(first) + 1)
