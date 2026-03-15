import frappe
from frappe.tests.utils import FrappeTestCase


def create_device_type():
	if frappe.db.exists("Device Type", {"device_type": "_Test Device"}):
		return frappe.get_doc("Device Type", {"device_type": "_Test Device"})

	device = frappe.new_doc("Device Type")
	device.device_type = "_Test Device"
	device.description = "Test device for unit testing"
	device.insert()
	return device


def create_technician():
	if frappe.db.exists("Technician", {"technician_name": "_Test Technician"}):
		return frappe.get_doc("Technician", {"technician_name": "_Test Technician"})

	tech = frappe.new_doc("Technician")
	tech.technician_name = "_Test Technician"
	tech.employee_id = "EMP-TEST-001"
	tech.status = "Active"
	tech.insert()
	return tech

def create_spare_part(**kwargs):

	if frappe.db.exists("Spare Part", {"part_code": kwargs.get("part_code", "TT")}):
		return frappe.get_doc("Spare Part", {"part_code": kwargs.get("part_code", "TT")})
	
	spare = frappe.new_doc("Spare Part")
	spare.part_name=kwargs.get("part_name", "_test")
	spare.part_code=kwargs.get("part_code", "TT")
	spare.stock_qty=kwargs.get("stock_qty", 10)
	spare.unit_cost=kwargs.get("u_cost", 20)
	spare.selling_price=kwargs.get("s_cost", 40)
	spare.insert()
	return spare




def create_job_card(device, technician,**kwargs):

	job_data = {
		"doctype": "Job Card",
		"customer_name": "_Test Customer",
		"customer_phone": kwargs.get("customer_phone", "8907654321"),
		"device_type": device.name,
		"assigned_technician": technician.name,
		"problem_description": "Test issue",
		"status": "Draft"
	}

	job = frappe.get_doc(job_data)
	job.insert()
	return job


class TestJobCard(FrappeTestCase):

	def setUp(self):
		self.device = create_device_type()
		self.tech = create_technician()
		self.spare=create_spare_part()
		self.job = create_job_card(self.device, self.tech)
		print(self.device)
		print(self.tech)


	def test_job_card_happy_path_insert(self):

		self.assertTrue(frappe.db.exists("Job Card", self.job.name))
		self.assertEqual(self.job.docstatus, 0)
		self.assertEqual(self.job.device_type, self.device.name)
		self.assertEqual(self.job.assigned_technician, self.tech.name)


	def test_job_card_status_default(self):
		self.assertEqual(self.job.status, "Draft")


	def test_phone_validation(self):
		invalid_numbers = [
			"1111",              
			"1234567890123",   
			"564321ABCD09"]
		for phone in invalid_numbers:
			with self.assertRaises(frappe.ValidationError):
				create_job_card(self.device, self.tech,customer_phone=phone)

		job = create_job_card(self.device, self.tech,customer_phone="9876543201")
		self.assertTrue(frappe.db.exists("Job Card", job.name))


	def test_spare_part_sellingprice_constraints(self):

		with self.assertRaises(frappe.ValidationError):
			create_spare_part(
				part_code="_low",
				stock_qty=5,
				u_cost=500,
				s_cost=409
			)
		with self.assertRaises(frappe.ValidationError):
			create_spare_part(
				part_code="_equal",
				stock_qty=5,
				u_cost=500,
				s_cost=500
			)
		valid = create_spare_part(
			part_code="_high",
			stock_qty=5,
			u_cost=500,
			s_cost=501
		)
		self.assertTrue(valid.name)

	
	def test_final_amount_computation(self):

		spare = create_spare_part(
			part_code="_calc_test",
			stock_qty=10,
			u_cost=200,
			s_cost=300
		)

		job = create_job_card(self.device, self.tech)
		qty=2
		price=300
		job.append("parts_used", {
			"part": spare.name,
			"quantity": qty,
			"unit_price": price
		})
		job.save()

		expected_parts_total = qty * price
		settings = frappe.get_single_value("QuickFix Settings",'default_labour_charge')
		expected_final_amount = expected_parts_total + settings

		self.assertEqual(job.parts_total, expected_parts_total)
		self.assertEqual(job.final_amount, expected_final_amount)



	def test_in_repair_status_transition_guard(self):

		self.job.status = "In Repair"
		self.job.assigned_technician = None

		with self.assertRaises(frappe.ValidationError) as context:
			self.job.save()
		self.job.reload()

		self.assertIn("technician", str(context.exception).lower())
		self.job.assigned_technician = self.tech.name
		self.job.save()
		self.job.status = "In Repair"
		self.assertEqual(self.job.status, "In Repair")


	def tearDown(self):

		# logs = frappe.get_all(
		# 	"Audit Log",
		# 	filters={"doctype_name": ["in", ["Job Card",]]},
		# 	pluck="name"
		# )

		# for log in logs:
		# 	frappe.delete_doc("Audit Log", log, force=True)

		jobs = frappe.get_all(
		"Job Card",
		filters={"customer_name": "_Test Customer"},
		pluck="name")

		for job in jobs:
			doc = frappe.get_doc("Job Card", job)
			doc.status = "Draft"
			doc.save(ignore_permissions=True)
			frappe.delete_doc("Job Card", job, force=True)


		if frappe.db.exists("Device Type", self.device.name):
			frappe.delete_doc("Device Type", self.device.name, force=True)

		if frappe.db.exists("Technician", self.tech.name):
			frappe.delete_doc("Technician", self.tech.name, force=True)

		parts = frappe.get_all(
		"Spare Part",
		filters={"part_name": ["like", "_%"]},
		pluck="name")

		for part in parts:
			frappe.delete_doc("Spare Part", part, force=True)

		frappe.db.commit()