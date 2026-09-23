// Copyright (c) 2026, Santhiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stay Card", {
	refresh(frm) {
        if (frm.is_new()){
            return
        }
        frappe.call({method: "pawpass.api.share_stay_card",args: {stay_card_name: frm.doc.name,user_email: ""},
            callback: function(r) {
                console.log(r.message);
            }
        });
        // frappe.call({method:"pawpass.api.transfer_stays",args:{from_attendant: frm.assigned_attendant,to_attendant: frm.assigned_attendant},
        // callback(r){
        //     console.log(r.message);
        // }
        // })

	},
});
