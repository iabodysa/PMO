import frappe

app_name = "pmo"
app_title = "PMO"
app_publisher = "PMO CSB"
app_description = "Follow-up app for units, entities, action items and weekly submissions"
app_email = ""
app_license = "mit"


def has_app_permission():
	return bool(
		{"PMO Manager", "Project Manager", "Project Specialist", "System Manager"} & set(frappe.get_roles())
	)


add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/pmo/images/pmo.svg",
		"title": app_title,
		"route": "/desk/pmo",
		"has_permission": "pmo.hooks.has_app_permission",
	}
]

scheduler_events = {
	"daily": [
		"pmo.tasks.reconcile_next_update_due",
	],
}
