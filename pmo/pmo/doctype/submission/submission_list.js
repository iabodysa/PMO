// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.listview_settings["Submission"] = {
	add_fields: ["status", "cycle_due_date"],
	get_indicator(doc) {
		const overdue =
			doc.status === "Draft" &&
			doc.cycle_due_date &&
			doc.cycle_due_date < frappe.datetime.get_today();

		if (overdue) {
			return [__("Pending / Overdue"), "red", "status,=,Draft"];
		}

		const colours = { Draft: "gray", Submitted: "blue", Reviewed: "green" };
		return [__(doc.status), colours[doc.status] || "gray", "status,=," + doc.status];
	},
};
