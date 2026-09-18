import frappe

DOCTYPE = "Challenge"
FIELD = "is_continuous"


def execute():
	if not frappe.db.table_exists(DOCTYPE) or not frappe.db.has_column(DOCTYPE, FIELD):
		return
	if frappe.get_meta(DOCTYPE, cached=False).get_field(FIELD):
		return

	names = frappe.db.sql_list(f"select name from `tab{DOCTYPE}` where `{FIELD}` = 1 order by name")
	if not names:
		return

	frappe.log_error(
		title=f"PMO retired {DOCTYPE}.{FIELD}, {len(names)} rows await a Watch Item",
		message="\n".join(names),
	)
