import frappe
from frappe.model.utils.rename_field import rename_field

DOCTYPES = ("Action Item", "Challenge", "Watch Item")
OLD = "torch_bearer"
NEW = "owner_unit"


def execute():
	for doctype in DOCTYPES:
		if not frappe.db.table_exists(doctype):
			continue
		if not frappe.db.has_column(doctype, OLD):
			continue
		if not frappe.get_meta(doctype, cached=False).get_field(NEW):
			frappe.throw(f"{doctype} carries no {NEW} field, so {OLD} cannot be renamed")
		if _filled(doctype, NEW):
			continue

		expected = _filled(doctype, OLD)
		rename_field(doctype, OLD, NEW)
		carried = _filled(doctype, NEW)
		if carried != expected:
			frappe.throw(f"{doctype}.{NEW} carries {carried} of {expected} {OLD} values")


def _filled(doctype, fieldname):
	return frappe.db.sql(
		f"select count(*) from `tab{doctype}` where `{fieldname}` is not null and `{fieldname}` != ''"
	)[0][0]
