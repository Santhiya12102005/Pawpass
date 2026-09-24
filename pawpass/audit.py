import frappe

def log_change(doc, method=None):

    if doc.doctype == "Audit Log":   # prevent running the method infinitily
        return

    action_map = {
        "on_update": "Save",
        "on_submit": "Submit",
        "on_cancel": "Cancel"
    }

    audit = frappe.new_doc("Audit Log")

    audit.doctype_name = doc.doctype
    audit.document_name = doc.name
    audit.action = action_map.get(method, method)
    audit.user = frappe.session.user
    audit.timestamp = frappe.utils.now()

    audit.insert(ignore_permissions=True)