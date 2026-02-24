# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	pass







def permission_query_conditions(user):
	if "QF Technician" in frappe.get_roles(user):
		frappe.log_error("jhgfvc",frappe.db.escape(user))
		return "assigned_technician.user = {0}".format(frappe.db.escape(user))