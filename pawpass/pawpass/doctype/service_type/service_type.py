# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SERVICETYPE(Document):
	def validate(self):
		if self.base_rate <= 0:
			frappe.throw("Base Rate must be greater than 0")
