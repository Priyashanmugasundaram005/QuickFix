# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from datetime import datetime


class SparePart(Document):
	def autoname(self):
		if self.part_code:
			self.part_code=self.part_code.upper()
		year=datetime.now().year
		count=frappe.db.count("Spare Part")+1
		secq=str(count).zfill(4)
		self.name=f"{self.part_code}-'PART'-{year}-{secq}"

	def validate(self):
		if self.selling_price<self.unit_cost:
			frappe.throw("Selling Price should be greater than Unit Cost")
		


@frappe.whitelist(allow_guest=True)
def rename():

	#Using merge=True in frappe.rename_doc is dangerous because it permanently combines two records into one, which can unintentionally overwrite data,
	#  mix histories, and corrupt linked references if the documents represent different real-world entities.
	frappe.rename_doc("Technician",'TECH-0020','TECH-0001',merge=False)
	
