// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.ui.form.on("Action Item", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(__("Add Progress Update"), () => {
			frappe.new_doc("Progress Update", {
				reference_doctype: frm.doc.doctype,
				reference_name: frm.doc.name,
			});
		});

		frm.add_custom_button(__("View Updates"), () => {
			frappe.route_options = {
				reference_doctype: frm.doc.doctype,
				reference_name: frm.doc.name,
			};
			frappe.set_route("List", "Progress Update");
		});

		frm.add_custom_button(
			frm.doc.pmo_coordinator
				? __("Reassign PMO Coordinator")
				: __("Assign PMO Coordinator"),
			() => {
				frappe.prompt(
					{
						fieldname: "pmo_coordinator",
						fieldtype: "Link",
						options: "User",
						label: __("PMO Coordinator"),
						default: frm.doc.pmo_coordinator,
						reqd: 1,
					},
					(values) =>
						frm
							.set_value("pmo_coordinator", values.pmo_coordinator)
							.then(() => frm.save()),
					__("PMO Coordinator"),
					__("Assign")
				);
			}
		);
	},
});
