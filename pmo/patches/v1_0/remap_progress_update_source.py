import frappe

DOCTYPE = "Progress Update"
FIELD = "update_source"
MAPPING = (("Torch Bearer", "Owner Unit"), ("Entity", "Related Entity"))


def execute():
	if not frappe.db.table_exists(DOCTYPE) or not frappe.db.has_column(DOCTYPE, FIELD):
		return

	field = frappe.get_meta(DOCTYPE, cached=False).get_field(FIELD)
	survivors = [option for option in (field.options or "").split("\n") if option] if field else []
	if not survivors:
		return

	for old, new in MAPPING:
		if old in survivors:
			continue
		if new not in survivors:
			frappe.throw(f"{DOCTYPE}.{FIELD} offers no {new} option to carry {old} rows")
		frappe.db.sql(f"update `tab{DOCTYPE}` set `{FIELD}` = %s where `{FIELD}` = %s", (new, old))

	unknown = [
		value
		for value in frappe.db.sql_list(
			f"select distinct `{FIELD}` from `tab{DOCTYPE}` where `{FIELD}` is not null and `{FIELD}` != ''"
		)
		if value not in survivors
	]
	if unknown:
		frappe.throw(f"{DOCTYPE}.{FIELD} still holds {', '.join(sorted(unknown))}")
