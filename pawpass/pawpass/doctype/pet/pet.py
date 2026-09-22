# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils import getdate


class PET(Document):
	def autoname(self):
		year = getdate(self.date_of_birth).year		
		prefix = f"{self.pet_code.upper()}-PET-{year}-"
		suffix = getseries(prefix,4)
		self.name = f"{prefix}{suffix}"
	