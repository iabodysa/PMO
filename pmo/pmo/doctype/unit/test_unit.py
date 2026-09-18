# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from pmo.patches.v1_0.migrate_region_into_unit import execute as migrate_region_into_unit

SHARED_CHILD_NAME = "Planning Department"
FIRST_REGION = "Riyadh Region"
SECOND_REGION = "Makkah Region"
MIGRATED_LINK_SUBJECT = "Region link carried through the migration"


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


class TestRegionMigrationIntoUnit(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Region",
				"module": "Custom",
				"custom": 1,
				"autoname": "field:region_name",
				"naming_rule": "By fieldname",
				"fields": [
					{
						"label": "Region Name",
						"fieldname": "region_name",
						"fieldtype": "Data",
						"reqd": 1,
						"unique": 1,
					},
					{
						"label": "Is All Regions",
						"fieldname": "is_all_regions",
						"fieldtype": "Check",
					},
				],
				"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}],
			}
		).insert()

		for region_name in (FIRST_REGION, SECOND_REGION):
			frappe.get_doc({"doctype": "Region", "region_name": region_name}).insert()

		cls.action_item = frappe.get_doc(
			{
				"doctype": "Action Item",
				"subject": MIGRATED_LINK_SUBJECT,
				"owner_unit": make_unit("Region Migration Owner Unit", unit_type="Department").name,
			}
		).insert()
		frappe.db.set_value(
			"Action Item", cls.action_item.name, "region", FIRST_REGION, update_modified=False
		)

		migrate_region_into_unit()

	@classmethod
	def tearDownClass(cls):
		frappe.db.rollback()
		if frappe.db.exists("DocType", "Region"):
			frappe.delete_doc("DocType", "Region", force=True, ignore_permissions=True)
		frappe.db.commit()
		frappe.db.sql_ddl("drop table if exists `tabRegion`")
		super().tearDownClass()

	def migrated_unit(self, region_name):
		return frappe.db.get_value(
			"Unit",
			{"unit_name": region_name, "unit_type": "Region"},
			["name", "is_group", "is_active"],
			as_dict=True,
		)

	def test_every_region_row_becomes_an_active_group_unit_of_type_region(self):
		for region_name in (FIRST_REGION, SECOND_REGION):
			unit = self.migrated_unit(region_name)
			self.assertIsNotNone(unit)
			self.assertEqual(unit.is_group, 1)
			self.assertEqual(unit.is_active, 1)

	def test_an_action_item_region_link_names_the_migrated_unit_instead_of_the_old_region_row(self):
		unit = self.migrated_unit(FIRST_REGION)

		self.assertEqual(frappe.db.get_value("Action Item", self.action_item.name, "region"), unit.name)
		self.assertNotEqual(unit.name, FIRST_REGION)

	def test_the_standalone_region_doctype_is_removed_once_its_rows_live_in_the_unit_tree(self):
		self.assertFalse(frappe.db.exists("DocType", "Region"))
