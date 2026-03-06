// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

frappe.query_reports["Spare Parts Inventory"] = {
	"filters": [

	],

	formatter:function(value,row,column,data,default_formatter){
		value=default_formatter(value,row,column,data)
		if (column.fieldname=='st_qty' && data){
			if(data.st_qty<=data.reorder_level){
				value = `<span style="color:red">${value}</span>`;
			}

		}
		return value
			
	}
};
