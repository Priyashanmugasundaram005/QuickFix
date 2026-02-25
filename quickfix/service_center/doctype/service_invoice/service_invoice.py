# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceInvoice(Document):
	pass

def has_permission(doc,user):
	if user=="Administrator":
		return True
	
	if not "QF Manager" in frappe.get_roles(user):
		if doc.payment_status!='Paid':
			return False
