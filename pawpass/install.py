import frappe

def after_install():
    service_types = [
        {"service_name": "Bath & Brush", "base_rate": 500},
        {"service_name": "Nail Trim", "base_rate": 200},
        {"service_name": "Deshedding Treatment", "base_rate": 700},
        {"service_name": "Overnight Boarding", "base_rate": 1500},
    ]

    for service in service_types:
        if not frappe.db.exists("SERVICE TYPE",{"service_name": service["service_name"]}):
            doc = frappe.new_doc("SERVICE TYPE")
            doc.service_name = service["service_name"]
            doc.base_rate = service["base_rate"]
            doc.insert(ignore_permissions=True)

    paw_settings = frappe.get_single("PAWPASS SETTINGS")

    if paw_settings.is_new():
        paw_settings.insert(ignore_permissions=True)

    frappe.msgprint("PawPass setup completed successfully")
