// Copyright (c) 2026, priii and contributors
// For license information, please see license.txt

frappe.query_reports["Spare Parts Inventory"] = {
	"filters": [

	],

	formatter:function(value,row,column,data,default_formatter){
		value=default_formatter(value,row,column,data)
		
			if(data && data.st_qty<=Number(data.reorder_lvl)){
				console.log("88888")
				return `<span style="background-color:#ffcccc;display:block;">${value}</span>`;
			}

		
		return value
			
	}
};
