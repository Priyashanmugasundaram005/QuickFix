# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
import re
from frappe.utils import nowdate


class JobCard(Document):
	pass
	def valuybidate(self):
		total=0
		frappe.log_error("111")
		if self.customer_phone:
			frappe.log_error("2222",self.customer_phone)
			if not re.fullmatch(r"\d{10}",self.customer_phone):
				frappe.throw("Enter valid 10 digit Phone number")

		required_statuses = ["In Repair", "Ready for Delivery", "Delivered"]

		if self.status in required_statuses and not frappe.db.exists("Technician",{'status':'Active','name':self.assigned_technician}):
			frappe.throw("Assigned Technician not available. Select other technician")

		

		
		for row in self.parts_used:
			qty = row.quantity or 0
			rate = row.unit_price or 0
			row.total_price = qty * rate
			total+=row.total_price
		self.parts_total=total	
		if not self.labour_charge:
			self.labour_charge=frappe.db.get_single_value("QuickFix Settings",'default_labour_charge')
		self.final_amount=self.parts_total+self.labour_charge

		# if not self.device_model:
		# 	frappe.msgprint("Customer Name is required (Controller)")
		# frappe.msgprint("Controller validate executed")
            

        

	def before_submit(self):
		if self.status!="Ready for Delivery":
			frappe.throw("Job is not ready for delivery")
		for row in self.parts_used:
			stock=frappe.get_value("Spare Part",row.part,['stock_qty'])
			if stock<row.quantity:
				frappe.throw("Stock unavailable")


	def on_submit(self):
		self.end_job_ready_email()
		for part in self.parts_used:
			current=frappe.db.get_value("Spare Part",part,'stock_qty')or 0
			#  We use frappe.db.set_value for stock deduction because this is asystem-initiated update during document submission.
			#  Direct DB updates do not enforce user permissions and are safe here since the user already has permission to submit the Job Card.

			frappe.db.set_value("Spare Part",part,'stock_qty',current- part.quantity)

		new_ent=frappe.new_doc("Service Invoice")
		new_ent.job_card=self.name
		new_ent.customer_name=self.customer_name
		new_ent.invoice_date=nowdate()
		new_ent.labour_charge=self.labour_charge
		new_ent.parts_total=self.parts_total
		new_ent.total_amount=self.final_amount
		new_ent.payment_status=self.payment_status
		new_ent.docstatus=1
		new_ent.insert(ignore_permissions=True)

	def mail(self=None, customer_email=None):
		frappe.log_error("customer_emailllllllll",customer_email)
		frappe.sendmail(recipients=customer_email,message="Your job is ready")

	def end_job_ready_email(self):
		frappe.log_error("maill",self.customer_email)
		frappe.enqueue(method=self.mail,queue="short",customer_email=[self.customer_email])
		



	def on_cancel(self):
		self.status='Cancelled'

		for part in self.parts_used:
			current=frappe.db.get_value("Spare Part",part,'stock_qty') or 0
			frappe.db.set_value("Spare Part",part,'stock_qty',current+part.quantity)

		invoice=frappe.get_value("Service Invoice",{'job_card':self.name,'docstatus':1})    # Not required 
		if invoice:
			inv=frappe.get_doc("Service Invoice",invoice)
			inv.cancel()

	def on_trash(self):
		if not self.status in ['Draft','Cancelled']:
			frappe.throw(f"Cannot delete job card with status `{self.status}'.""Only Job Cards with Draft or Cancelled status can be deleted.")

	# def on_update(self):
	# 	frappe.log_error("loggggggggg")
	# 	self.save()








def permission_query_conditions(user):
	if user=="Administrator":
		return""
	if "QF Technician" in frappe.get_roles(user):
		technician_names = frappe.get_all(
            "Technician",
            filters={"user": user},
            pluck="name"
        )
		if technician_names:
			return f"""
        `tabJob Card`.assigned_technician IN (
            SELECT name FROM `tabTechnician`
            WHERE user = {frappe.db.escape(user)}
        )
    """
		else:
			return "1=0" 
        
	
