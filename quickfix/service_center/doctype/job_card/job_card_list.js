frappe.listview_settings['Job Card'] = {
    add_fields: ['status', 'docstatus', 'final_amount', 'priority'],// add fields wont make changes in the view

    colors: {
        "Open": "blue",
        "Pending Diagnosis": "orange",
        "In Repair": "orange",
        "Ready for Delivery": "green",
        "Delivered": "green",
        "Cancelled": "red"
    },
    has_indicator_for_draft: true,

    get_indicator(doc) {
        if (doc.status) {
            return [
                doc.status,
                this.colors[doc.status],
                "status ,=," + doc.status
            ];
        }
    },
    // formatters: {
    //     final_amount(value) {
    //         if (!value) return "";                                                               // Formatting without this code
    //         return format_currency(value, frappe.defaults.get_default("currency"));
    //     }
    // },

    button: {
    show(doc) {
        return doc.status === "In Repair";
    },
    get_label() {
        return "Mark Ready";
    },
    get_description() {
        return "Mark job as Ready for Delivery";
    },
    action(doc) {

        frappe.db.set_value("Job Card", doc.name, "status", "Ready for Delivery")
            .then(() => {

                frappe.show_alert({
                    message: ("Status updated to Ready for Delivery"),
                    indicator: "green"
                });

                frappe.listview.refresh();
            });

    }
}

    // if(doc.status ==='In Repair'){
    //     frameElement.add_custom_button("Job ready")
    // }



};