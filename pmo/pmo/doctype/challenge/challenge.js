// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.ui.form.on("Challenge", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Add Progress Update"), () => {
			frappe.new_doc("Progress Update", {
				reference_doctype: "Challenge",
				reference_name: frm.doc.name,
			});
		});

		frm.add_custom_button(__("View Updates"), () => {
			frappe.set_route("List", "Progress Update", {
				reference_doctype: "Challenge",
				reference_name: frm.doc.name,
			});
		});

		frm.add_custom_button(__("Create Action Item"), () => {
			const values = {
				owner_unit: frm.doc.owner_unit,
				region: frm.doc.region,
				priority: frm.doc.priority,
				description: __("Raised from Challenge {0}: {1}", [frm.doc.name, frm.doc.title]),
			};

			if (frm.doc.related_entity) {
				values.entity = frm.doc.related_entity;
			}

			frappe.new_doc("Action Item", values);
		});
	},
});
