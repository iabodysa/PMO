# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe

from pmo.pmo.doctype.watch_item.watch_item import refresh_next_update_due


def reconcile_next_update_due():
	for name in frappe.get_all("Watch Item", filters={"status": "Active"}, pluck="name"):
		refresh_next_update_due(name)
