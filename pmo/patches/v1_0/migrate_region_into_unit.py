import frappe

LINK_DOCTYPES = ("Action Item", "Challenge", "Watch Item")
LINK_FIELD = "region"
UNIT_TYPE = "Region"


def execute():
	if not frappe.db.table_exists("Region"):
		return

	regions = frappe.db.sql("select name, region_name from `tabRegion` order by name", as_dict=True)
	if regions:
		_require_unit_can_hold_regions()

	mapping = {}
	created = []
	for region in regions:
		unit_name = region.region_name or region.name
		existing = frappe.db.get_value("Unit", {"unit_name": unit_name, "unit_type": UNIT_TYPE}, "name")
		if existing:
			mapping[region.name] = existing
			continue
		unit = frappe.get_doc(
			{
				"doctype": "Unit",
				"unit_name": unit_name,
				"unit_type": UNIT_TYPE,
				"is_group": 1,
				"is_active": 1,
			}
		)
		unit.insert(ignore_permissions=True)
		mapping[region.name] = unit.name
		created.append(region.name)

	for doctype in _linked_doctypes():
		for old, new in mapping.items():
			if old == new:
				continue
			frappe.db.set_value(doctype, {LINK_FIELD: old}, LINK_FIELD, new, update_modified=False)

	for doctype in _linked_doctypes():
		dangling = frappe.db.sql(
			f"select count(*) from `tab{doctype}` t"
			f" where t.`{LINK_FIELD}` is not null and t.`{LINK_FIELD}` != ''"
			f" and not exists (select 1 from `tabUnit` u where u.name = t.`{LINK_FIELD}`)"
		)[0][0]
		if dangling:
			frappe.throw(f"{doctype}.{LINK_FIELD} holds {dangling} values that name no Unit")

	if created:
		_log_all_regions_flag(mapping)

	if frappe.db.exists("DocType", "Region"):
		frappe.delete_doc("DocType", "Region", force=True, ignore_permissions=True)


def _require_unit_can_hold_regions():
	if not frappe.db.table_exists("Unit"):
		frappe.throw("Unit is missing, so Region rows cannot be migrated")
	field = frappe.get_meta("Unit", cached=False).get_field("unit_type")
	options = (field.options or "").split("\n") if field else []
	if UNIT_TYPE not in options:
		frappe.throw(f"Unit.unit_type offers no {UNIT_TYPE} option, so Region rows cannot be migrated")


def _linked_doctypes():
	for doctype in LINK_DOCTYPES:
		if frappe.db.table_exists(doctype) and frappe.db.has_column(doctype, LINK_FIELD):
			yield doctype


def _log_all_regions_flag(mapping):
	if not frappe.db.has_column("Region", "is_all_regions"):
		return
	flagged = frappe.db.sql_list("select name from `tabRegion` where is_all_regions = 1 order by name")
	if not flagged:
		return
	frappe.log_error(
		title=f"PMO Region migration dropped is_all_regions on {len(flagged)} rows",
		message="\n".join(f"{name} -> {mapping.get(name, name)}" for name in flagged),
	)
