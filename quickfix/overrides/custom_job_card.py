from quickfix.service_center.doctype.job_card.job_card import JobCard
import frappe
from frappe.utils import nowdate



class CustomJobCard(JobCard):
    pass
    def validate(self):
        # super().validate()
        frappe.log_error("valll")
        self._check_urgent_unassigned()

 # ---------------- MRO & super()----------------
# MRO decides the order in which parent classes are executed.
# When overriding a DocType class, your class runs before Frappe's core class.
# If you skip super(), core validations and other app logic will NOT run,
# causing broken workflows and data issues.
# → Always call super() to preserve the execution chain.


# ---------------- override_doctype_class vs doc_events----------------
# override_doctype_class → Use when you must modify core controller behavior.
# doc_events             → Use for safe hooks like logging, alerts, automation.

    def _check_urgent_unassigned(self):
        if self.priority=="Urgent" and not self.assigned_technician:
            settings=frappe.get_single_value("QuickFix Settings",'manager_email')
            frappe.log_error("sett",settings)
            frappe.enqueue("quickfix.utils.send_urgent_alert",job_card=self.name,manager=settings)



def create_audit_log(doctype_name, document_name=None, action="api_call"):
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doctype_name,
        "document_name": document_name,
        "action": action,
        "user": frappe.session.user,
        "timestamp": nowdate(),
    }).insert(ignore_permissions=True)

def log(doc, method):
    allowed = [
        'Technician', 'Device Type', 'Spare Part',
        'Job Card', 'QuickFix Settings',
        'Service Invoice', 'Part Usage Entry'
    ]

    if doc.doctype not in allowed:
        return

    create_audit_log(doc.doctype, doc.name, method)

# def validate_job_card(doc, method):
#     # Hook-level validation
#     if doc.priority == "Urgent" :
#         frappe.msgprint("Urgent jobs must have a technician (Hook)")

#     frappe.msgprint("Hook validate executed")

def install():
    data=[

        {
            "average_repair_hours": 24,
            "description": "Smartphone description",
            "device_type": "Smartphone",
        },
        {
            "average_repair_hours": 48,
            "description": "Laptop description",
            "device_type": "Laptop",
        },
        {
            "average_repair_hours": 24,
            "description": "Tablet description",
            "device_type": "Tablet",
        }]

    for row in data:
        if not frappe.db.exists("Device Type",row['device_type']):
            device=frappe.get_doc(
                {
                    "doctype":"Device Type",
                    "device_type":row["device_type"],
                    "description":row["description"],
                    "average_repair_hours":row["average_repair_hours"]
                }
            )
            device.insert(ignore_permissions=True)

    # For Single Doctype
    settings = frappe.get_single("QuickFix Settings")
    settings.shop_name = "QuickFix"
    settings.manager_email = "yashinishan2005.com"
    settings.default_labour_charge = 500
    settings.low_stock_threshold = 5
    settings.low_stock_alert_enable = 1
    settings.save(ignore_permissions=True)

    print("Successfully Executed after_install hook")


def before_uninstall():
    data = frappe.get_all("Job Card",
            filters={
                "docstatus":1
            }
        )
    if data:
        raise frappe.ValidationError(
            _("App Uninstall Restricted Due to Submitted Job Cards — Cancel Required Before Removal."))


def extend_bootinfo(bootinfo):
    settings = frappe.get_single("QuickFix Settings")

    # Add custom values to bootinfo
    bootinfo.quickfix_shop_name = settings.shop_name
    bootinfo.quickfix_manager_email = settings.manager_email


    
