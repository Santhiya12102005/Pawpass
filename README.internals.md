Group D:
Don't leak data:
    -> frappe.get_all() method bypasses the permissions for the user but in get_list() it checks the permission that the user have permission to view the record this is the main difference 
    -> If the user has no permission for the record but has the permission in whitelisted method that user try to retrive the records from the doctype if doctype has get_all() it doesn't check the permission so any user can change the record but in get_list it restrict the user from accessing the records.

Group B:
B2C->   def validate(self):
            self.services_total = sum(r.line_total for r in self.service_lines)
            self.save()
            pet = frappe.get_doc("Pet", self.pet)
            pet.total_stays += 1
            pet.save()

            -> In this method save() is called inside the validate method in this case after save document lifecycle triggers the validate method again this will call save() so this happens reccursively that means infinity times. do not give save() inside the validate method
            ->Another bug is updating the pet.total_stays += 1 value after updating the value it will trigger validate because after the update we need to sav ethe record in each save validate will called and calculated values will recalculated that will affect the field values.

        solution:
        we can write on_update() to calculate the pet.total_stays 
        def validate(self):
            self.services_total = sum(r.line_total for r in self.service_lines)
        def on_update():
            pet = frappe.get_doc("Pet", self.pet)
            pet.total_stays += 1

B2d->  Optimistic locking
    If two user working on the same page one user modified the doctype specification in second user try to save or modify frappe will show an error "This Has been modified refresh the page to continue the process..", it will calculated by the meta data fields by the time that field is created. It helps to prevent the data multiple data inserted for same doctype

Group E:
on_update() — the recursion pitfall:
    -> In every time of the updation multiple records will be created and in UI it shows "Maximum recursion limit exceed".
    -> In the document lifecycle if any updation is performed it will automatically triggers the save which means save() -> on_update() -> self.save() -> on_update() -> self.save() -> infinity times..
solution simply:
def on_update(self):
    frappe.msgprint("Updated Successfully")
    frappe.db.set_value()

E2: autoname & Renaming:
    -> if merge=false means it renames the name and also rename the fields that is linked in another doctypes
    -> if merge=true means it will combine the old record to new record

E3: get_doc() vs get_value()
    -> In get_doc() it get all the meta data of the document
    -> In get_value() it get only the specific value we entered in the method 
    -> for Attendant controller's on_update methon we can go with get_value() it will directly get the specific value.

Group H:
frappe.call() inside validate():
    -> In this scenario frappe.call() call the server/API method, inside the validate it must complete the task after that the next task will execute, it will check already available values, synchronous validation and throw error if needed
    -> frappe.call() in refresh or onload the response will saved and respond it will fetching and  asynchronous work

Group J:
Difference between frappe.get_all() and before_print:
    -> Calling frappe.get_all() directly inside a Jinja template mixes database access with presentation logic. The query is executed every time the template is rendered and can lead to unnecessary database queries, and it will bypass the permissions.
    -> Before_print will fetch and prepare the required data in before_print() and store it on the document in precomputed_field, Jinja template then displays only the precomputed data it is safe for print format, easy for maintain and test.

Group L
L1: Normal API 
URL: http://127.0.0.1:8000/api/resource/Stay%20Card/PC-2026-00034
response:
{"data":{"name":"PC-2026-00034","owner":"Administrator","creation":"2026-09-25 14:17:09.502205","modified":"2026-09-25 14:17:31.246011","modified_by":"Administrator","docstatus":1,"idx":0,"workflow_state":"Ready for Pickup","pet":"JOHN-PET-2020-0001","owner_name":"John","owner_phone":"9876542312","checkin_date":"2026-09-25","expected_checkout_date":"2026-09-30","purpose":"Grooming Only","vaccination_status":"Valid","assigned_attendant":"ATT-0002","services_total":0.0,"final_amount":0.0,"payment_status":"Unpaid","status":"Ready for Pickup","doctype":"Stay Card","service_lines":[{"name":"4k7d0dpndo","owner":"Administrator","creation":"2026-09-25 14:17:09.502205","modified":"2026-09-25 14:17:31.246011","modified_by":"Administrator","docstatus":1,"idx":1,"service_type":"Service Groom","service_name":"Service Groom","rate":12000.0,"quantity":1.0,"line_total":0.0,"parent":"PC-2026-00034","parentfield":"service_lines","parenttype":"Stay Card","doctype":"Service Line"}]}}

Error: 
URL: http://127.0.0.1:8000/api/resource/Stay%20Card/PC-2026-00039
response:
{"exc_type":"DoesNotExistError","_server_messages":"[\"{\\\"message\\\":\\\"Stay Card PC-2026-00039 not found\\\",\\\"as_table\\\":false,\\\"title\\\":\\\"Message\\\",\\\"indicator\\\":\\\"red\\\",\\\"raise_exception\\\":1,\\\"__frappe_exc_id\\\":\\\"16bc20266349f0f85453d99a4fe157442ce8fde3a3df80bc7df4b2d9\\\"}\"]"}

Custom API:
URL: http://127.0.0.1:8000/api/method/pawpass.api.get_stay_summary?stay_card_name=PC-2026-00032
response:
{"message":{"name":"PC-2026-00032","pet_id":"LILY","owner_name":"Kaviya","owner_phone":"6754268296","checkin_date":"2026-09-25","purpose":"Grooming Only","assigned_attendent":"ATT-0002","final_amount":0.0}}

Group K
K2: N+1 problem
stay_cards = frappe.get_all("Stay Card", fields=["name","assigned_attendant"])
for sc in stay_cards:
    att = frappe.get_doc("Attendant", sc.assigned_attendant)
    print(att.attendant_name, att.phone)

    -> In this method, If there are 100 Stay Cards, this executes roughly 101 database queries: 1 query to fetch the Stay Cards, then 100 additional queries to fetch each Attendant this is the N+1 problem

Fix:
    -> We can fix this with left join the ATTENDANT table with Stay Card

    StayCard = DocType("Stay Card")
    Attendant = DocType("Attendant")

    stay_cards = (frappe.qb.from_(StayCard).left_join(Attendant).on(StayCard.assigned_attendant == Attendant.me).select(StayCard.name,StayCard.assigned_attendant,Attendant.attendant_name,Attendant.phone)).run(as_dict=True)

    for sc in stay_cards:
        print(sc.attendant_name, sc.phone)