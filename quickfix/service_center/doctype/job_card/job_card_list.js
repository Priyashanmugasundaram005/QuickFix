frappe.listview_settings['Job Card']={
    add_fields:['status','docstatus','final_amount','priority'],// add fields wont make changes in the view

    colors : {
        "Open": "blue",
        "Pending Diagnosis": "orange",
        "In Repair": "orange",
        "Ready for Delivery": "green",
        "Delivered": "green",
        "Cancelled": "red"
    },
    
    get_indicator(doc){
        if(doc.status)
        {
            return [
                doc.status,
                this.colors[doc.status],
                "status ,=,"+doc.status
            ];
        }
    },
    formatters: {
        final_amount(value) {
            if (!value) return "";
            return format_currency(value, frappe.defaults.get_default("currency"));
        }
    },

    button:{
        show(doc){
            return doc.status==="In Repair";
            // return doc.name;
        },
        get_label(){
            return("Mark Ready");
        },
        get_description(){
 return "23456"
        },
        action(doc){
            frappe.call(
                {
                method: "frappe.client.set_value",
                args: {
                    doctype: "Job Card",
                    name: doc.name,
                    fieldname: "status",
                    value: "Ready for Delivery"
                },
                callback:()=>{
                    frappe.show_alert({
                        message: __("Status updated to Ready for Delivery"),
                        indicator: "green"
                    });
                    frappe.listview.refresh();

                }
                }
            )

        }
    }

    // if(doc.status ==='In Repair'){
    //     frameElement.add_custom_button("Job ready")
    // }



};