// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	setup(frm) {
        value=frappe.db.get_single_value("QuickFix Settings",'default_labour_charge')
        .then(value=>{
            frm.set_value('labour_charge',value)
        })


	},
});
