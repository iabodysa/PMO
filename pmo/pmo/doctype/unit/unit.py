# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

from frappe.utils.nestedset import NestedSet


class Unit(NestedSet):
	nsm_parent_field = "parent_unit"
