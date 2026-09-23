# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries,make_autoname
from frappe.utils import getdate,today,add_days


class PET(Document):
	def autoname(self):
		# year = getdate(self.date_of_birth).year		
		# prefix = f"{self.pet_code.upper()}-PET-{year}-"
		# suffix = getseries(prefix,4)
		# self.name = f"{prefix}{suffix}"
		if self.pet_code:
			self.name = f"{self.pet_code.upper()}"
		else:
			self.name = make_autoname("PET-.YYYY.-.####")
		
		

