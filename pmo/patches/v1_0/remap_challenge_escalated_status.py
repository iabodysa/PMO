import frappe

DOCTYPE = "Challenge"
FIELD = "status"
OLD = "Escalated"
NEW = "Open"


def execute():
	if not frappe.db.table_exists(DOCTYPE) or not frappe.db.has_column(DOCTYPE, FIELD):
		return

	field = frappe.get_meta(DOCTYPE, cached=False).get_field(FIELD)
	survivors = [option for option in (field.options or "").split("\n") if option] if field else []
	if not survivors or OLD in survivors:
		return
	if NEW not in survivors:
		frappe.throw(f"{DOCTYPE}.{FIELD} offers no {NEW} option to carry {OLD} rows")

	names = frappe.db.sql_list(f"select name from `tab{DOCTYPE}` where `{FIELD}` = %s order by name", OLD)
	if not names:
		return

	if frappe.db.has_column(DOCTYPE, "is_escalated"):
		frappe.db.sql(f"update `tab{DOCTYPE}` set is_escalated = 1 where `{FIELD}` = %s", OLD)
	if frappe.db.has_column(DOCTYPE, "escalated_on"):
		frappe.db.sql(
			f"update `tab{DOCTYPE}` set escalated_on = date(modified)"
			f" where `{FIELD}` = %s and escalated_on is null",
			OLD,
		)

	frappe.db.sql(f"update `tab{DOCTYPE}` set `{FIELD}` = %s where `{FIELD}` = %s", (NEW, OLD))

	frappe.log_error(
		title=f"PMO retired {DOCTYPE} status {OLD}, {len(names)} rows now {NEW}",
		message="\n".join(names),
	)
