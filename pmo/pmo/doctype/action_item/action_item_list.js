// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.listview_settings["Action Item"] = {
	add_fields: ["status", "due_date"],
	get_indicator(doc) {
		if (
			doc.status !== "Completed" &&
			doc.due_date &&
			doc.due_date < frappe.datetime.get_today()
		) {
			return [__("Overdue"), "red", "due_date,<,Today|status,!=,Completed"];
		}

		const colours = {
			"Not Started": "gray",
			"In Progress": "orange",
			Completed: "green",
		};

		return [
			__(doc.status, null, "Action Item"),
			colours[doc.status],
			"status,=," + doc.status,
		];
	},
};
