// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.ui.form.on("Watch Item", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Add Progress Update"), () => {
			frappe.new_doc("Progress Update", {
				reference_doctype: frm.doctype,
				reference_name: frm.doc.name,
			});
		});

		frm.add_custom_button(__("View Updates"), () => {
			frappe.set_route("List", "Progress Update", {
				reference_doctype: frm.doctype,
				reference_name: frm.doc.name,
			});
		});
	},
});
