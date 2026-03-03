// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Job Card", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Job Card", {
    
    setup(frm) {
        value = frappe.db.get_single_value("QuickFix Settings", 'default_labour_charge')
            .then(value => {
                frm.set_value('labour_charge', value)
            })

        },
    
    

    device_type: function (frm) {
        console.log("yesss")
        frm.call('technician')
            .then(r => {
                tech = r.message
                frm.set_query('assigned_technician', () => {
                    return {
                        filters: {
                            name: ['in', tech]

                        }

                    }
                })

            })



    },
    refresh(frm) {
        add_color(frm);
        button(frm);
        name = frappe.boot.quickfix_shop_name
        if (name)
            frm.page.set_title(
                `Shop : ${name}`
            )


        // frm.page.set_indicator(
        //         __("Shop: {0}", [frappe.boot.quickfix_shop_name]),
        //         "blue"
        //     );

        frm.add_custom_button("Reject Job",()=>{
            let dialog =new frappe.ui.Dialog({
                title:'Reject',
                fields:[
                    {
                        label: 'Rejection Reason',
                        fieldname: 'reason',
                        fieldtype: 'Small Text',
                        reqd:1
                    }
                ],
                primary_action_label:'Submit',
                primary_action(values){
                    console.log(values)
                    frappe.msgprint("Job Rejected");
                    dialog.hide();
                }
            });
            dialog.show();
    });

    if (frm.doc.docstatus !=1){
    frm.add_custom_button("Transfer Technician",()=>
    {
        
        frappe.prompt([{

            label: 'New Technician',
            fieldname: 'new',
            fieldtype: 'Link',
            options:'Technician',
            reqd:1,
            get_query:() => {
                    return {
                        filters: {
                            specialization:frm.doc.device_type

                        }

                    }
                }

            }

        ],(values)=>{
            frappe.confirm("Do you need to proceed with this Technician",()=>{
                frm.trigger('assigned_technician')
                frm.call('new_tech',{new_technician:values.new})
            })
        }
    )
    }


)}

// if (!frappe.user.has_role("System Manager")) {                    // Shipped JS
//             console.log("App JS Loaded");
//             frm.toggle_display('customer_phone', false);
//         } else {
//             frm.toggle_display('customer_phone', true);
//         }



},
    status: add_color,
    onload(frm) {
        console.log("innn")
        frm.call('real')
        frappe.realtime.on("job_ready", (data) => {
            
            // if (data.name === frm.doc.name) {
            console.log("ouuu")
                frappe.show_alert({
                    message:("Job is Ready"),
                    indicator: "green"
                });
            // }
        });
    },
    assigned_technician: function (frm) {
    {
        console.log("jhuib")
        frm.call('validate')
    }
}

});


function button(frm) {
    console.log("iuygfvb")
    if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1) {
        frm.add_custom_button(("Mark as Delivered"))
    }
}

function add_color(frm) {
    frm.dashboard.clear_headline();
    const colors = {
        "Open": "blue",
        "Pending Diagnosis": "orange",
        "In Repair": "orange",
        "Ready for Delivery": "green",
        "Delivered": "green",
        "Cancelled": "red"
    };

    if (frm.doc.status)
        frm.dashboard.add_indicator(('status: ') + frm.doc.status, colors[frm.doc.status] || 'gray')
}


frappe.ui.form.on('Part Usage Entry', {
    part: function (frm, cdt, cdn) {
        console.log("patrs")
        let list = []
        console.log(list)
        frm.doc.parts_used.forEach(parts => {
            if (list.includes(parts.part))
                frappe.throw(`${parts.part} is already added`)
            else
                list.push(parts.part)
        }
        )
    },
    
    quantity: function (frm, cdt, cdn) {
        
        // frm.doc.parts_used.forEach(p=>{
        console.log("poiuhb")
        const row = locals[cdt][cdn]
        const price = row.unit_price * row.quantity
        frappe.model.set_value(cdt,cdn,'total_price', price)
        let total=0
        let tot=0
        frm.doc.parts_used.forEach(r=>
        {
            total+=r.total_price || 0
        }

        )
        frm.set_value('parts_total',total)
        tot=frm.doc.parts_total+frm.doc.labour_charge
        frm.set_value('final_amount',tot)
        

    }

})

