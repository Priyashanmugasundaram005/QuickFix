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




	]
};
