# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = [
		{
			'fieldname': 'part_name',
			'label': ('Part Name'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'part_code',
			'label': ('Part Code'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'device_type',
			'label': ('Device Type'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'st_qty',
			'label': ('Stock Quantity'),
			'fieldtype': 'Int'
		},
		{
			'fieldname': 'reorder_lvl',
			'label': ('Reorder Level'),
			'fieldtype':'Float'
		},
		{
			'fieldname': 'unit_cost',
			'label': ('Unit Cost'),
			'fieldtype':'Currency',
			'precision':2
		},
		{
			'fieldname': 'sp',
			'label': ('Selling Price'),
			'fieldtype':'Currency',
			'precision':2
		},
		{
			'fieldname': 'margin',
			'label': ('Margin %'),
			'fieldtype':'Percentage',
			'precision':2
		},
			
	]

	data=[]

	spare_part=frappe.db.get_all("Spare Part",fields=['part_name','part_code','compatible_device_type','stock_qty','reorder_level','unit_cost','selling_price'])
	for spare in spare_part:
		frappe.log_error("ppppp",spare.reorder_level)
		reorder=spare.reorder_level
		frappe.log_error("11111111",reorder)
		
		if spare.unit_cost and spare.selling_price:
			
			margin=((spare.selling_price-spare.unit_cost)/spare.unit_cost)*100
		else:
			margin=0
		data.append(
			{
				'part_name':spare.part_name,
				'part_code':spare.part_code,
				'device_type':spare.compatible_device_type,
				'st_qty':spare.stock_qty,
				'reorder_lvl':round(reorder,2),
				'unit_cost':round(spare.unit_cost,2),
				'sp':round(spare.selling_price,2),
				'margin':round(margin,2)
			}
		)
		tot=len(spare_part)
		below=0
		invent=0
		tot_stock=0
		sell_tot=0
		frappe.log_error("22222222",spare.reorder_level)

		for spare in spare_part:
			stock = spare.stock_qty or 0
			tot_stock+=stock
			reorder = spare.reorder_level 
			unit_cost = spare.unit_cost or 0
			sell=spare.selling_price or 0
			if stock<reorder:
				below+=1
			invent+=stock*unit_cost
			sell_tot+=stock*sell
		frappe.log_error("333333",spare.reorder_level)

	data.append(
		{
			'part_name':"Total",
			'st_qty':tot_stock,
			'unit_cost':invent,
			'sp':sell_tot
		
		}
	)
	frappe.log_error("44",spare.reorder_level)
		
	summary=[
		{'label':"Total Parts",'value':tot,'datatype':'Int'},
		{'label':"Below Reorder",'value':below,'datatype':'Int'},
		{'label':"Total Inventory Value",'value':invent,'datatype':'Currency'}
	]







	
	return columns, data, None,None,summary
