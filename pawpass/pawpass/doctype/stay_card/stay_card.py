# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today,add_days


class StayCard(Document):
	
	def validate(self):	
		
		val_exp = frappe.db.get_value("PET",self.pet,"vaccination_expiry")
		grace = frappe.db.get_single_value("PAWPASS SETTINGS","vaccination_grace_days") or 0
		exp_day = add_days(val_exp, grace)
		if getdate(exp_day) < getdate(today()):
			self.vaccination_status = "Expired"
			if self.status != "Draft":
				frappe.throw("The stay cannot proceed because vaccination has expired")
		else:
			self.vaccination_status = "Valid"

		if self.purpose and self.purpose == "Boarding":
			if getdate(self.expected_checkout_date) < getdate(self.checkin_date):
				frappe.throw("Expected Checkout Date must be after Checkin Date")

		total = 0
		for row in self.service_lines or []:
			row.line_total = (row.rate or 0)*(row.quantity or 0)
			total += row.line_total
		self.services_total = total
		self.final_amount = total

	def before_submit(self):
		if self.status != "Ready for Pickup":
			frappe.throw("Status Must be Ready for Pickup") 

		if not self.service_lines or len(self.service_lines)==0:
			frappe.throw("Add Atleast one Service line")

		if self.vaccination_status != "Valid":
			frappe.throw("Vaccination Status must be Valid")
		
	def on_submit(self):
		total_stay = frappe.db.get_value("PET",self.pet,"total_stays") or 0
		frappe.db.set_value("PET",self.pet,"total_stays",total_stay+1) 
		frappe.db.set_value("PET",self.pet,"last_visit_date",self.checkin_date)


	def on_cancel(self):
		self.status = "Cancelled"
		total = frappe.db.get_value("PET",self.pet,"total_stays") or 0
		if total != 0:
			frappe.db.set_value("PET",self.pet,"total_stays",total-1)

	# 	card_name = frappe.db.get_value("Invoice","stay_card")
	# 	if card_name == self.name:
	# 		frappe.db.set_value("Invoices","stay_card","")
	
	def on_trash(self):
		if self.status in ["Cancelled","Draft"]:
			frappe.throw("Staus not in Cancelled or Draft")
		
	# def on_update(self):
	# 	self.save()

	