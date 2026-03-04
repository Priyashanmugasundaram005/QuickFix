# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff


def execute(filters=None):
	ft=filters.get("from_date")
	to=filters.get("to_date")
	technician=filters.get("technician")
	base_filters={}
	if technician:
		base_filters["assigned_technician"] = technician
	if ft and to:
		base_filters['creation']=['between',[ft,to]]


	columns = [

		{
			'fieldname': 'technician',
			'label': ('Technician'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'total_jobs',
			'label': ('Total Jobs'),
			'fieldtype': 'Int'
		},
		{
			'fieldname': 'completed',
			'label': ('Completed'),
			'fieldtype': 'Int'
		},
		{
			'fieldname': 'avg_turn_day',
			'label': ('Avg Turnaround Days'),
			'fieldtype': 'Float'
		},
		{
			'fieldname': 'revenue',
			'label': ('Revenue'),
			'fieldtype': 'Currency'
		},
		{
			'fieldname': 'completion_rate',
			'label': ('Completion Rate %'),
			'fieldtype': 'Float'
		},
	]

	device=frappe.get_all("Device Type",pluck='name')
	for dev in device:
		columns.append({
			'label': (dev),
			'fieldtype': 'Int'

		})


	data=[]
	if technician:
		technician_list=[technician]
	else:
		technician_list=frappe.get_all("Technician",pluck='name')

	for tech in technician_list:

		base_filters["assigned_technician"] = tech
		
		jobs=frappe.db.get_all("Job Card",filters=base_filters,fields=['name','status','creation','delivery_date','device_type','labour_charge'])
		total=len(jobs)
		rev=0
		comp=0
		turnar=0
		device_counts = {dev.lower(): 0 for dev in device}
		frappe.log_error("devvv",device_counts)

		for job in jobs:
			frappe.log_error("helooooo",job.device_type)


			if job.device_type.lower() in device_counts:
				frappe.log_error("helooooo",job.device_type)
				device_counts[job.device_type.lower()] += 1
				
			rev+=job.labour_charge or 0
			if job.status=='Ready for Delivery':
				comp+=1

			if job.delivery_date:
				turnar+=date_diff(job.delivery_date,job.creation)
		
		avg=(turnar/comp if comp else 0)
		
		completion_rate = (comp / total )*100 if total else 0

		row={
			
				'technician':tech,
				'total_jobs':total,
				'completed':comp,
				'revenue':rev,
				'avg_turn_day':round(avg,2),
				'completion_rate':round(completion_rate,2),	
			
		}

		frappe.log_error("lpoiuytfv",device_counts)
		row.update(device_counts)
		data.append(row)

		
	return columns, data
