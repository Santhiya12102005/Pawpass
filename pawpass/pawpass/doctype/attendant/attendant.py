# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ATTENDANT(Document):
	def on_update(self):
        frappe.rename_doc("ATTENDANT","ATT-003","ATT-004",merge=False)

	
