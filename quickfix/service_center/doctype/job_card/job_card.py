# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt


import frappe,requests,json
from frappe.model.document import Document
import re
from frappe.utils import nowdate


class JobCard(Document):
	
	@frappe.whitelist()
	def validate(self):
		total=0
		self.company=self.final_amount
		frappe.log_error("111")
		if self.customer_phone:
			frappe.log_error("2222",self.customer_phone)
			if not re.fullmatch(r"\d{10}",self.customer_phone):
				frappe.throw("Enter valid 10 digit Phone number")

		required_statuses = ["In Repair", "Ready for Delivery", "Delivered"]

		if self.status in required_statuses and not frappe.db.exists("Technician",{'status':'Active','name':self.assigned_technician}):
			frappe.throw("Assigned Technician not available. Select other technician")
		if self.status=="In Repair" and self.estimated_cost==0:
			frappe.throw("Estimated cost cannot be zero when status is in In Repair")

		

		
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
			stock=frappe.get_value("Spare Part",row.part,['stock_qty'])or 0
			if stock<row.quantity:
				frappe.throw("Stock unavailable ",frappe.ValidationError)
		self.status="Delivered"


	def on_submit(self):
		
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

		self.maill()

	def maill(self):
		if frappe.flags.in_tests:
			return
		frappe.enqueue(
		method=self.send_job_ready_email,
		queue="short")

		pdf=frappe.get_print(self.doctype,self.name,"Job Card Receipt",as_pdf=True)
		frappe.sendmail(recipients=self.customer_email,attachments=[{
		"fname": "Job_Card_Receipt.pdf",
		"fcontent": pdf
		}])

		frappe.enqueue(
		self.send_webhook,
		job_card_name=self.name,
		retry_count=0,
		queue="default",
		timeout=60
	)
		
	def send_webhook(self,job_card_name,retry=0):

		settings = frappe.get_single("QuickFix Settings")

		if not settings.webhook_url:
			return
		payload = {
			"event": "job_submitted",
			"job_card": self.name,
			"customer": self.customer_name,
			"amount": self.final_amount
		}

		try:
			requests.post(settings.webhook_url, json=payload, timeout=5)

		except Exception as e:
			frappe.log_error(f"Webhook failed: {e}", "Webhook Error")

			if retry < 3:
				frappe.enqueue(
					"quickfix.api.send_webhook",
					job_card_name=job_card_name,
					retry=retry+1,
					enqueue_after_commit=True,
					timeout=60
				)



	def mail(self=None, customer_email=None):
		frappe.log_error("customer_emailllllllll",customer_email)
		frappe.sendmail(recipients=customer_email,message="Your job is ready")

	def send_job_ready_email(self):
		frappe.log_error("maill",self.customer_email)
		frappe.enqueue(method=self.mail,queue="short",customer_email=[self.customer_email])

		
		


	# @frappe.whitelist()
	# def on_cancel(self):
	# 	# if frappe.flags.in_tests:
	# 	# 	return
	# 	self.status='Cancelled'

	# 	for part in self.parts_used:
	# 		current=frappe.db.get_value("Spare Part",part,'stock_qty') or 0
	# 		frappe.db.set_value("Spare Part",part,'stock_qty',current+part.quantity)

	# 	invoice=frappe.get_value("Service Invoice",{'job_card':self.name,'docstatus':1})    # Not required 
	# 	if invoice:
	# 		inv=frappe.get_doc("Service Invoice",invoice)
	# 		inv.cancel()

	def on_update(self):
		frappe.cache().delete_value("job_card_status_chart")
    	

	def on_trash(self):
		
		if not self.status in ['Draft','Cancelled']:
			frappe.throw(f"Cannot delete job card with status `{self.status}'.""Only Job Cards with Draft or Cancelled status can be deleted.")

	# def on_update(self):
	# 	frappe.log_error("loggggggggg")
	# 	self.save()

	@frappe.whitelist()
	def technician(self):
		frappe.log_error(self.device_type)
		tech=frappe.get_all("Technician",{'status':'Active','specialization':self.device_type},pluck='name')
		frappe.log_error("rtyu",tech)
		return tech

	@frappe.whitelist()
	def cancellll(self):
		frappe.log_error("11111111111111111")
		self.cancel()

	@frappe.whitelist()
	def real(self):
		frappe.log_error("reallll")
		frappe.publish_realtime(
		event="job_ready",
		message={"name": 'name'})

	@frappe.whitelist()
	def new_tech(self,new_technician):
		frappe.log_error(new_technician)
		self.assigned_technician=new_technician
		self.save(ignore_permissions=True)

	def before_print(self,print_settings=None):
   		self.print_summary = f"{self.customer_name} - {self.device_type} {self.device_model}"	

	

	# def generate_monthly_revenue_report(self,year):
	# 	months = range(1, 13)
	# 	for i, month in enumerate(months, 1):
	# 		frappe.publish_progress(
	# 		percent=round(i/12*100),
	# 		title="Generating Revenue Report",
	# 		description=f"Processing month {month}..."
	# 		)










def permission_query_conditions(user):
	if user=="priyashanmugasundaram2005@gmail.com":
		return""
	# if "QF Technician" in frappe.get_roles(user):
	# 	technician_names = frappe.get_all(
    #         "Technician",
    #         filters={"user": user},
    #         pluck="name"
    #     )
	# 	if technician_names:
	# 		return f"""
    #     `tabJob Card`.assigned_technician IN (
    #         SELECT name FROM `tabTechnician`
    #         WHERE user = {frappe.db.escape(user)}
    #     )
    # """
	# 	else:
	# 		return "1=0" 
        
	
