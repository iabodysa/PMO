# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


SHARED_CHILD_NAME = "Planning Department"
FIRST_REGION = "Riyadh Region"
SECOND_REGION = "Makkah Region"


def make_unit(unit_name, unit_type=None, parent_unit=None, is_group=0):
	return frappe.get_doc(
		{
			"doctype": "Unit",
			"unit_name": unit_name,
			"unit_type": unit_type,
			"parent_unit": parent_unit,
			"is_group": is_group,
		}
	).insert()


class TestUnitTree(IntegrationTestCase):
	def test_two_units_may_carry_the_same_unit_name_under_two_different_parents(self):
		first_region = make_unit(FIRST_REGION, unit_type="Region", is_group=1)
		second_region = make_unit(SECOND_REGION, unit_type="Region", is_group=1)

		first_child = make_unit(SHARED_CHILD_NAME, unit_type="Department", parent_unit=first_region.name)
		second_child = make_unit(SHARED_CHILD_NAME, unit_type="Department", parent_unit=second_region.name)

		self.assertNotEqual(first_child.name, second_child.name)
		self.assertEqual(first_child.unit_name, second_child.unit_name)
		self.assertEqual(
			{first_child.name, second_child.name},
			set(frappe.get_all("Unit", filters={"unit_name": SHARED_CHILD_NAME}, pluck="name")),
		)
		self.assertEqual(
			[first_region.name, second_region.name],
			[first_child.parent_unit, second_child.parent_unit],
		)
