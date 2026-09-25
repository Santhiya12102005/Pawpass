# Copyright (c) 2026, Santhiya and Contributors
# See license.txt

import frappe
import unittest

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class TestStayCard(unittest.TestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
	def test_happy_path(self):
		pet = frappe.get_doc({
			"doctype":"PET",
			"pet_name":"Ken",
			"species":"Dog",
			"owner_name":"John",
			"owner_phone":"9876543212",
			"vaccination_expiry":"2026-09-29"
		}).insert()
		doc = frappe.get_doc({
			"doctype":"Stay Card",
			"pet":pet.name,
			"checkin_date":"2026-09-25"
		}).insert()

		self.assertEqual(doc.docstatus,0)

	def test_vaccination_exp(self):
		pet = frappe.get_doc({
			"doctype":"PET",
			"pet_name":"Kavi",
			"species":"Dog",
			"owner_name":"John wil",
			"owner_phone":"9876543212",
			"vaccination_expiry":"2026-09-01"
		}).insert()
		doc = frappe.get_doc({
			"doctype":"Stay Card",
			"pet":pet.name,
			"checkin_date":"2026-09-25"
		}).insert(ignore_if_duplicate=True)

		self.assertEqual(doc.docstatus,0)

	def test_stype_rate(self):

			service = frappe.get_doc({
				"doctype": "SERVICE TYPE",
				"service_name": "Test Service Valid",
				"base_rate": 1
			}).insert(ignore_if_duplicate=True)

			self.assertEqual(service.base_rate, 1)

	def test_fa_computation(self):

		service1 = frappe.get_doc({
			"doctype": "SERVICE TYPE",
			"service_name": "Test Bath",
			"base_rate": 500
		}).insert(ignore_if_duplicate=True)

		service2 = frappe.get_doc({
			"doctype": "SERVICE TYPE",
			"service_name": "Test Nail Trim",
			"base_rate": 200
		}).insert(ignore_if_duplicate=True)

		pet = frappe.get_doc({
			"doctype": "PET",
			"pet_name": "Penny",
			"species": "Dog",
			"owner_name": "Lisa",
			"owner_phone": "9876543212",
			"vaccination_expiry": "2026-09-30"
		}).insert(ignore_if_duplicate=True)

		doc = frappe.get_doc({
			"doctype": "Stay Card",
			"pet": pet.name,
			"checkin_date": "2026-09-25",
			"service_lines": [
				{
					"service_type": service1.name,
					"rate": 500,
					"quantity": 3
				},
				{
					"service_type": service2.name,
					"rate": 200,
					"quantity": 2
				}
			]
		}).insert(ignore_if_duplicate=True)


		self.assertEqual(doc.service_lines[0].line_total, 1500)
		self.assertEqual(doc.service_lines[1].line_total, 400)
		self.assertEqual(doc.services_total, 1900)
		self.assertEqual(doc.final_amount, 1900)

	def test_service_line(self):
		service = frappe.get_doc({
			"doctype": "SERVICE TYPE",
			"service_name": "Brushing",
			"base_rate": 150
		}).insert(ignore_if_duplicate=True)
		pet = frappe.get_doc({
			"doctype": "PET",
			"pet_name": "Jen",
			"species": "Dog",
			"owner_name": "Lily",
			"owner_phone": "9876543212",
			"vaccination_expiry": "2026-09-30"
		}).insert(ignore_if_duplicate=True)
		doc = frappe.get_doc({
			"doctype": "Stay Card",
			"pet": pet.name,
			"checkin_date": "2026-09-25",
			"service_lines": [
				{
					"service_type": service.name,
					"rate": 500,
					"quantity": 3
				}
			],
			"status":"Ready for Pickup"
		}).insert(ignore_if_duplicate=True)

		doc.before_submit()
		doc.on_submit()

		self.assertTrue(doc.name)

	def test_on_cancel_pet(self):
		pet = frappe.get_doc({
			"doctype": "PET",
			"pet_name": "Tommy",
			"species": "Dog",
			"owner_name": "John",
			"owner_phone": "9876543210",
			"vaccination_expiry": "2026-12-31",
			"total_stays": 0
		}).insert()

		before_submit = frappe.db.get_value("PET", pet.name, "total_stays") or 0

		stay = frappe.get_doc({
			"doctype": "Stay Card",
			"pet": pet.name,
			"status": "Ready for Pickup",
			"service_lines": [{
				"service_type": "Brushing",
				"quantity": 1,
				"rate": 500
			}]
		}).insert()

		stay.submit()
		after_submit = frappe.db.get_value("PET", pet.name, "total_stays")
		self.assertEqual(after_submit, before_submit + 1)
		stay.cancel()
		after_cancel = frappe.db.get_value("PET", pet.name, "total_stays")
		self.assertEqual(after_cancel, before_submit)

	def test_duplicate_invoice(self):
		stay = self.test_happy_path()
		before = frappe.db.count("Invoice",{"stay_card": stay.name})
		stay.on_submit()
		after = frappe.db.count("Invoice",{"stay_card": stay.name})
		self.assertEqual(before, 1)
		self.assertEqual(after, 1)