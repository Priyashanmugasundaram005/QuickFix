# Copyright (c) 2026, priii and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DeviceType(Document):
	def validate(self):
		frappe.utils.logger.set_log_level("INFO")
		logger=frappe.logger("quickfix")
		logger.info("Infoooo")
		logger.warning("Warning")
		logger.error("Errorrr")
