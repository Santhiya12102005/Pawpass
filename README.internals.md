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