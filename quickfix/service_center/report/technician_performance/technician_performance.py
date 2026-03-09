# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff


def execute(filters=None):

	ft = filters.get("from_date")
	to = filters.get("to_date")
	technician = filters.get("technician")

	conditions = ""
	values = {}

	if technician:
		conditions += " AND assigned_technician = %(technician)s"
		values["technician"] = technician

	if ft and to:
		conditions += " AND creation BETWEEN %(from_date)s AND %(to_date)s"
		values["from_date"] = ft
		values["to_date"] = to

	columns = [
		{
			'fieldname': 'technician',
			'label': ('Technician'),
			'fieldtype': 'Link',
			'options': 'Technician',
			'width': 150
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
			'fieldtype': 'Currency',
			'width': 150
		},
		{
			'fieldname': 'completion_rate',
			'label': ('Completion Rate %'),
			'fieldtype': 'Percentage',
			"precision": 2
		},
	]

	device = frappe.get_all("Device Type", pluck='name')

	for dev in device:
		columns.append({
			'label': dev,
			'fieldname': dev.lower(),
			'fieldtype': 'Int'
		})

	# Single optimized SQL query
	jobs = frappe.db.sql(f"""
		SELECT
			assigned_technician,
			device_type,
			status,
			creation,
			delivery_date,
			IFNULL(labour_charge,0) AS labour_charge
		FROM `tabJob Card`
		WHERE 1=1 {conditions}
	""", values, as_dict=True)

	data_map = {}

	for job in jobs:

		tech = job.assigned_technician

		if tech not in data_map:
			data_map[tech] = {
				'technician': tech,
				'total_jobs': 0,
				'completed': 0,
				'revenue': 0,
				'turnaround': 0,
				**{dev.lower():0 for dev in device}
			}

		row = data_map[tech]

		row['total_jobs'] += 1
		row['revenue'] += job.labour_charge

		if job.status == "Ready for Delivery":
			row['completed'] += 1

		if job.delivery_date:
			row['turnaround'] += date_diff(job.delivery_date, job.creation)

		if job.device_type and job.device_type.lower() in row:
			row[job.device_type.lower()] += 1


	data = []

	for tech, row in data_map.items():

		comp = row['completed']
		total = row['total_jobs']

		avg = row['turnaround'] / comp if comp else 0
		completion_rate = (comp / total) * 100 if total else 0

		row['avg_turn_day'] = round(avg,2)
		row['completion_rate'] = round(completion_rate,2)

		del row['turnaround']

		data.append(row)

	labels = []
	total_list = []
	completed_list = []
	revenue = []

	best = None
	max_jobs = 0

	for r in data:
		labels.append(r.get("technician"))
		total_list.append(r.get("total_jobs"))
		completed_list.append(r.get("completed"))
		revenue.append(r.get("revenue"))

		if r.get("total_jobs",0) > max_jobs:
			max_jobs = r.get("total_jobs")
			best = r.get("technician")

	chart = {
		'title': "Total vs Completed per technician",
		'data': {
			'labels': labels,
			'datasets': [
				{
					'name': "Total",
					'values': total_list
				},
				{
					'name': "Completed Jobs",
					'values': completed_list
				},
			]
		},
		'type': 'bar',
		'height': 300,
	}

	tot = sum(total_list)
	reve = sum(revenue)

	summary = [
		{'label': 'Total Jobs', 'value': tot, 'datatype': 'Int'},
		{'label': 'Total Revenues', 'value': reve, 'datatype': 'Currency'},
		{'label': 'Best Technician', 'value': best, 'datatype': 'Data'}
	]

	return columns, data, None, chart, summary