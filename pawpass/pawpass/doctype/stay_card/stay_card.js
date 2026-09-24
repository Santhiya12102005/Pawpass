// Copyright (c) 2026, Santhiya and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Stay Card", {
// 	refresh(frm) {
//         if (frm.is_new()){
//             return
//         }
//         frappe.call({method: "pawpass.api.share_stay_card",args: {stay_card_name: frm.doc.name,user_email: ""},
//             callback: function(r) {
//                 console.log(r.message);
//             }
//         });
//         // frappe.call({method:"pawpass.api.transfer_stays",args:{from_attendant: frm.assigned_attendant,to_attendant: frm.assigned_attendant},
//         // callback(r){
//         //     console.log(r.message);
//         // }
//         // })

// 	},
// });

frappe.ui.form.on("Stay Card",{
    setup(frm) {
        frm.set_query("assigned_attendant", function () {
            let is_boarding = (frm.doc.purpose || "").toLowerCase().includes("boarding");
            return {
                filters: {
                    status:"Active",
                    "specialization.is_boarding":is_boarding?1:0
                }
            };
        });
    },
    refresh(frm){
        set_dashboard_indicator(frm);
        if (frm.doc.status=="Ready for Pickup" && frm.doc.docstatus == 1){
            frm.add_custom_button("Mark as Picked Up");
        }

        frm.add_custom_button("Cancel Stay",()=>{
            let d = new frappe.ui.Dialog({
                title:"Cancel Reason",
                fields: [
                    {
                        label:"Cancellation Reason",
                        fieldname:"cancellation_reason",
                        fieldtype:"Small Text",
                        reqd:1
                    }
                ],
                primary_action_label:"Send",
                primary_action(values){
                    frappe.msgprint("Cancelled Successfully");
                    d.hide();
                }
            });
            d.show()
        })
        frm.add_custom_button("Reassign Attendant",()=>{
            frappe.prompt({
                label:"New Attendant",
                fieldname: 'attendant',
                fieldtype: 'Link',
                options:"ATTENDANT",
                reqd:1
            }, (values) => {
                frappe.confirm("Are you sure want to confirm this reassign",()=>{
                    frappe.call({
                        method:"pawpass.api.reassign_attendant",
                        args:{stay_card:frm.doc.name,attendant:values.attendant},
                        callback(r){
                            frm.trigger("assigned_attendant");
                            frappe.msgprint("Attendant reassigned");
                        }
                    });
                });
            },"Reassign Attendant","Reassign");
        })
    },
    assigned_attendant(frm) {
        if (!frm.doc.assigned_attendant) return;

        frappe.db.get_value("ATTENDANT",frm.doc.assigned_attendant,"specialization").then(r => {
            let specialization = r.message.specialization || "";
            let purpose = frm.doc.purpose || "";
            let purpose_is_boarding = purpose.toLowerCase().includes("boarding");
            let attendant_is_boarding = specialization.toLowerCase().includes("boarding");
            if (purpose_is_boarding !== attendant_is_boarding) {
                frappe.msgprint(
                    `Warning: Selected attendant specialization (${specialization}) does not match the purpose (${purpose}).`
                );
            }
        });
    }
});
frappe.ui.form.on("Service Line", {
    quantity(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let total = (row.rate || 0) * (row.quantity || 0);
        frappe.model.set_value(cdt, cdn, "line_total", total).then(() => {
            calculate_service_total(frm);
        });
    }
});
function calculate_service_total(frm) {
    let total = 0;
    (frm.doc.service_lines || []).forEach(row => {
        total += row.line_total || 0;
    });
    frm.set_value("services_total", total);
    frm.set_value("final_amount", total);
}

function set_attendant_query(frm){
    let is_boarding = (frm.doc.purpose || "").toLowerCase().includes("boarding");
    frm.set_query("assigned_attendant",function(){
        return {filters:{status:"Active",is_boarding:is_boarding?1:0}};
    });
}

function set_dashboard_indicator(frm){
    if(frm.doc.status === "Cancelled"){
        frm.dashboard.add_indicator('Cancelled', 'red');
    }
    if(frm.doc.status === "Draft"){
        frm.dashboard.add_indicator('Draft', 'grey');
    }
    if(frm.doc.status === "Checked In"){
        frm.dashboard.add_indicator('Checked In', 'green');
    }
    if(frm.doc.status === "In Service"){
        frm.dashboard.add_indicator('In Service', 'blue');
    }
    if(frm.doc.status === "Ready for Pickup"){
        frm.dashboard.add_indicator('Ready for Pickup', 'green');
    }
    if(frm.doc.status === "Picked Up"){
        frm.dashboard.add_indicator('Picked Up', 'red');
    }
}

