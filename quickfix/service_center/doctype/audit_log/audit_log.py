# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class AuditLog(Document):
	pass
	
def log_in(login_manager):
	doc=frappe.get_last_doc("Activity Log")
	frappe.get_doc(
		{
			"doctype":"Audit Log",
			"doctype_name":"Activity Log",
			"document_name":doc.name,
			"action":"Login",
			"user":frappe.session.user,
			"timestamp":nowdate()
		}
	).insert(ignore_permissions=True)


def log_out(login_manager=None):
	doc=frappe.get_last_doc("Activity Log")
	frappe.get_doc(
		{
			"doctype":"Audit Log",
			"doctype_name":"Activity Log",
			"document_name":doc.name,
			"action":"Logout",
			"user":frappe.session.user,
			"timestamp":nowdate()
		}
	).insert(ignore_permissions=True)


