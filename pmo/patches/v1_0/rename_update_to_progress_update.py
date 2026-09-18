import frappe
from frappe.model.rename_doc import rename_doc

OLD = "Update"
NEW = "Progress Update"
RAW_DOCTYPE_NAME_COLUMNS = (("__global_search", "doctype"),)


def execute():
	old_exists = frappe.db.table_exists(OLD)
	new_exists = frappe.db.table_exists(NEW)

	if old_exists and new_exists:
		stranded = _count(OLD)
		if stranded:
			frappe.throw(f"`tab{OLD}` holds {stranded} rows while `tab{NEW}` already exists")
		_repoint_raw_tables()
		return

	if not old_exists:
		_repoint_raw_tables()
		return

	before = _count(OLD)

	rename_doc(
		"DocType",
		OLD,
		NEW,
		ignore_permissions=True,
		show_alert=False,
		rebuild_search=False,
	)
	frappe.reload_doc("pmo", "doctype", "progress_update", force=True)

	after = _count(NEW)
	if after != before:
		frappe.throw(f"rename carried {after} of {before} {OLD} rows into {NEW}")

	_repoint_raw_tables()


def _count(doctype):
	return frappe.db.sql(f"select count(*) from `tab{doctype}`")[0][0]


def _repoint_raw_tables():
	tables = frappe.db.get_tables(cached=False)
	for table, column in RAW_DOCTYPE_NAME_COLUMNS:
		if table not in tables:
			continue
		frappe.db.sql(f"update `{table}` set `{column}` = %s where `{column}` = %s", (NEW, OLD))
