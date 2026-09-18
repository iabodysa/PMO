// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.ui.form.on("Submission", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status !== "Reviewed") {
			frm.add_custom_button(__("Add Existing Item"), () => add_existing_item(frm));
		}

		frm.add_custom_button(__("Create Challenge"), () => {
			frappe.new_doc("Challenge", {
				owner_unit: frm.doc.unit,
				source_submission: frm.doc.name,
			});
		});
	},
});

function add_existing_item(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Add Existing Item"),
		fields: [
			{
				fieldname: "item_type",
				fieldtype: "Select",
				label: __("Item Type"),
				options: ["Action Item", "Challenge", "Watch Item"],
				reqd: 1,
			},
			{
				fieldname: "item",
				fieldtype: "Dynamic Link",
				label: __("Item"),
				options: "item_type",
				reqd: 1,
			},
			{
				fieldname: "line_update",
				fieldtype: "Small Text",
				label: __("Line Update"),
			},
		],
		primary_action_label: __("Add"),
		primary_action(values) {
			frm.add_child("lines", values);
			frm.refresh_field("lines");
			frm.dirty();
			dialog.hide();
		},
	});

	dialog.show();
}
