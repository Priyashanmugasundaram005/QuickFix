// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

frappe.query_reports["Technician Performance"] = {
	"filters": [
		{
			fieldname:'from_date',
			label:('From Date'),
			fieldtype:'Date'
		},
		{
			fieldname:'to_date',
			label:('To Date'),
			fieldtype:'Date'
		},
		{
			fieldname:'technician',
			label:('Technician'),
			fieldtype:'Link',
			options:'Technician'
		},




	],

	formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname == "completion_rate" && data) {

            if (data.completion_rate >= 90) {
                value = `<span style="color:green">${value}</span>`;
            }
            else if (data.completion_rate < 70) {
                value = `<span style="color:red">${value}</span>`;
            }
            else {
                value = `<span style="color:orange">${value}</span>`;
            }
        }

        return value;
    }
};
