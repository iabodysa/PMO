// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.listview_settings["Challenge"] = {
	get_indicator: function (doc) {
		const colors = {
			Open: "blue",
			"Under Handling": "orange",
			Stalled: "red",
			Resolved: "green",
			Closed: "green",
		};

		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	},
};
