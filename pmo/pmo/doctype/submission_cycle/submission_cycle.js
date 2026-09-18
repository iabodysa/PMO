// Copyright (c) 2026, PMO CSB and contributors
// For license information, please see license.txt

frappe.ui.form.on("Submission Cycle", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("View Submissions"), () => {
			frappe.set_route("List", "Submission", { submission_cycle: frm.doc.name });
		});

		if (frm.doc.status === "Open") {
			frm.add_custom_button(__("Generate Region Submissions"), () => {
				generate_region_submissions(frm);
			});
		}

		show_cycle_statistics(frm);
	},
});

function generate_region_submissions(frm) {
	frappe
		.call({
			method: "pmo.pmo.doctype.submission_cycle.submission_cycle.generate_region_submissions",
			args: { submission_cycle: frm.doc.name },
			freeze: true,
			freeze_message: __("Generating region submissions"),
		})
		.then(() => frm.refresh());
}

function show_cycle_statistics(frm) {
	frappe
		.call({
			method: "pmo.pmo.doctype.submission_cycle.submission_cycle.get_cycle_statistics",
			args: { submission_cycle: frm.doc.name },
		})
		.then((response) => {
			const stats = response.message;
			if (!stats) {
				return;
			}

			frm.dashboard.add_indicator(__("Total Regions: {0}", [stats.total_regions]), "blue");
			frm.dashboard.add_indicator(__("Submitted: {0}", [stats.submitted]), "green");
			frm.dashboard.add_indicator(
				__("Pending: {0}", [stats.pending]),
				stats.pending ? "orange" : "green"
			);
		});
}
