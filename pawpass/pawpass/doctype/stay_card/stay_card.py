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
        
        self.calculate_service_amount()
                
        # total = 0
        # for row in self.service_lines or []:
        #     total += row.line_total
        # self.services_total = total
        # self.final_amount = total
    def calculate_service_amount(self):
        services_total = 0

        for row in self.service_lines:
            row.line_total = (row.rate or 0) * (row.quantity or 0)
            services_total += row.line_total

        self.services_total = services_total
        self.final_amount = services_total


    def before_submit(self):
        if self.status not in ["Ready for Pickup","Picked Up"]:
            frappe.throw("Status Must be Ready for Pickup or Picked Up") 

        if not self.service_lines or len(self.service_lines)==0:
            frappe.throw("Add Atleast one Service line")

        if self.vaccination_status != "Valid":
            frappe.throw("Vaccination Status must be Valid")
        
    def on_submit(self):
        total_stay = frappe.db.get_value("PET",self.pet,"total_stays")
        frappe.db.set_value("PET",self.pet,"total_stays",total_stay+1) 
        frappe.db.set_value("PET",self.pet,"last_visit_date",self.checkin_date)
        if not frappe.db.exists("Invoice",{"stay_card": self.name}):
            invoice = frappe.new_doc("Invoice")
            invoice.stay_card = self.name
            invoice.invoice_number = self.name
            invoice.insert()
        frappe.enqueue("pawpass.pawpass.doctype.stay_card.stay_card.send_email",queue="short",timeout=300,stay_card_name=self.name,is_async=True,enqueue_after_commit=True)

    def on_cancel(self):
        self.status = "Cancelled"
        total_stay = frappe.db.get_value("PET",self.pet,"total_stays") or 0
        frappe.db.set_value("PET",self.pet,"total_stays",max(total_stay-1,0)) 
        
        inv = frappe.db.get_value("Invoice",{"stay_card":self.name},"name")
        if inv:
            invoice = frappe.get_doc("Invoice",inv)
            if invoice.docstatus == 1:
                invoice.cancel()
                frappe.msgprint(invoice.docstatus)
        

    # 	card_name = frappe.db.get_value("Invoice","stay_card")
    # 	if card_name == self.name:
    # 		frappe.db.set_value("Invoices","stay_card","")
    
    def on_trash(self):
        if self.status not in ["Cancelled","Draft"]:
            frappe.throw("Status must in Draft or Cancelled to delete")
        
    def on_update(self):
        # self.save() infinity recursion call
        pass

def send_email(stay_card_name):
    if not frappe.db.exists("Stay Card", stay_card_name):
        return
    doc = frappe.get_doc("Stay Card", stay_card_name)
    email = frappe.db.get_value("PET",doc.pet,"owner_email")
    if email:
        frappe.sendmail(recipients=[email],subject="Pet Stay is Completed Successfully",message="<p>Thank You!</p>")

def before_print(doc,method=None,print_settings=None):
    doc.print_summary=(f"{doc.owner_name} -"f"{doc.pet}")

