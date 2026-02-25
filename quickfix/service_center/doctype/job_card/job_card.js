// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Job Card", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Job Card", {
	setup(frm) {
        value=frappe.db.get_single_value("QuickFix Settings",'default_labour_charge')
        .then(value=>{
            frm.set_value('labour_charge',value)
        })


	},
});


frappe.ui.form.on('Part Usage Entry',{
    part:function(frm,cdt,cdn){
        console.log("patrs")
        let list=[]
        console.log(list)
        frm.doc.parts_used.forEach(parts=>{
            if(list.includes(parts.part))
                frappe.throw(`${parts.part} is already added`)
            else
                list.push(parts.part)
        }
        )
    }

})

