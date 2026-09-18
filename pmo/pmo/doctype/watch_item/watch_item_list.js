// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.listview_settings["Watch Item"] = {
	add_fields: ["status", "next_update_due"],
	get_indicator(doc) {
		const today = frappe.datetime.get_today();

		if (doc.status === "Active" && doc.next_update_due && doc.next_update_due < today) {
			return [__("Update Due"), "red", "next_update_due,<," + today];
		}

		const colours = {
			Active: "blue",
			Paused: "gray",
			Closed: "green",
		};

		return [__(doc.status, null, doc.doctype), colours[doc.status], "status,=," + doc.status];
	},
};
