import frappe
from frappe.query_builder import DocType
from frappe.utils import today,add_days

@frappe.whitelist()
def stay_card_permission(user=None):
    user = user or frappe.session.user

    if "PP Attendant" in frappe.get_roles(user):
        return f"""
            Exists (select 1 from `tabATTENDANT` a where a.name = `tabStay Card`.assigned_attendant and a.user = '{user}')"""

    return ""

@frappe.whitelist()
def share_stay_card(stay_card_name, user_email):

    frappe.share.add(doctype="Stay Card",name=stay_card_name,user=user_email,read=1)
    return{"message":"Successful","stay-card":stay_card_name,"user_email":user_email}

@frappe.whitelist()
def get_stay_cards_unsafe():
    return frappe.get_all("Stay Card",fields=["*"])

@frappe.whitelist()
def get_stay_cards_safe():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    Stay_cards = frappe.get_list("Stay Card",fields=["*"])

    if "PP Manager" not in roles:
        for sc in Stay_cards:
            sc.pop("owner_phone",None)
            sc.pop("owner_email",None)
    return Stay_cards

@frappe.whitelist()
def get_upcoming_checkouts():
    sc = DocType("Stay Card")
    result = frappe.qb.from_(sc).select(sc.name,sc.pet,sc.owner_name,sc.expected_checkout_date).where((sc.status.isin(["Checked In","In Service"])) & (sc.expected_checkout_date <= add_days(today(),2))).orderby(sc.expected_checkout_date).run(as_dict=True)
    return result

# @frappe.whitelist()
# def transfer_stays(from_attendant, to_attendant):
#     try:
#         frappe.db.sql("""
#         update `tabStay Card` set assigned_attendant = %s where assigned_attendant = %s and status in ('Checked In','In Service')""",(to_attendant,from_attendant))
#         frappe.db.commit()
#         return "Success"
#     except Exception:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(),"failed")
#         raise


@frappe.whitelist()
def reassign_attendant(stay_card, attendant):
    frappe.db.set_value("Stay Card",stay_card,"assigned_attendant",attendant)
    return "Attendant reassigned successfully"

@frappe.whitelist()
def get_stay_summary():
    stay_card_name = frappe.form_dict.get("stay_card_name")

    if not stay_card_name or not frappe.db.exists("Stay Card", stay_card_name):
        return {"error": "404 Not found"}

    doc = frappe.get_doc("Stay Card", stay_card_name)

    return {
        "name": doc.name,
        "pet_id": doc.pet,
        "owner_name": doc.owner_name,
        "owner_phone": doc.owner_phone,
        "checkin_date": doc.checkin_date,
        "purpose": doc.purpose,
        "assigned_attendent": doc.assigned_attendant,
        "final_amount": doc.final_amount
    }