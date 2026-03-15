from quickfix.service_center.doctype.job_card.job_card import JobCard
import frappe, requests,hmac, hashlib, json
from frappe.utils import nowdate,today,getdate




class CustomJobCard(JobCard):
    @frappe.whitelist()
    def validate(self):
        super().validate()
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



def create_audit_log(doc,doctype_name, document_name=None, action=None):
    frappe.log_error("audittttt")
    audit=frappe.new_doc("Audit Log")
    audit.doctype_name = doctype_name
    audit.document_name=document_name
    if doctype_name=="Scheduled Job Log" and doc.scheduled_job_type=="custom_job_card.check_low_stock":
        audit.action="low_stock_check"
    else:
        audit.action=action
    audit.user=frappe.session.user
    audit.timestamp= nowdate()
    audit.insert(ignore_permissions=True)
    frappe.db.commit()

def log(doc, method):
    allowed = [
        'Technician', 'Device Type', 'Spare Part',
        'Job Card', 'QuickFix Settings',
        'Service Invoice', 'Part Usage Entry',"Scheduled Job Log"
    ]

    if doc.doctype not in allowed:
        return

    create_audit_log(doc,doc.doctype, doc.name, method)

# def validate_job_card(doc, method):
#     # Hook-level validation
#     if doc.priority == "Urgent" :
#         frappe.msgprint("Urgent jobs must have a technician (Hook)")

#     frappe.msgprint("Hook validate executed")

def install():
    make_remarks()
    
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

def make_remarks():
    frappe.make_property_setter({
        "doctype":"Job Card",
        "fieldname":"remarks",
        "property":"bold",
        "value":1,
        "property_type":"check"})


def before_uninstall():
    data = frappe.get_all("Job Card",
            filters={
                "docstatus":1
            }
        )
    if data:
        raise frappe.ValidationError(
            ("App Uninstall Restricted Due to Submitted Job Cards — Cancel Required Before Removal.")
        )


def extend_bootinfo(bootinfo):
    settings = frappe.get_single("QuickFix Settings")

    # Add custom values to bootinfo
    bootinfo.quickfix_shop_name = settings.shop_name
    bootinfo.quickfix_manager_email = settings.manager_email


@frappe.whitelist()
def get_status_chart_data():
    data = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabJob Card`
        GROUP BY status
    """, as_dict=True)

    labels = []
    values = []

    for d in data:
        labels.append(d.status)
        values.append(d.count)

    return {
        "labels": labels,
        "datasets": [
            {"name": "Jobs", "values": values}
        ],
        "type":"bar"
    }

def check_low_stock():
    last_run = frappe.db.get_value("Audit Log",
    {"action":"low_stock_check","timestamp":getdate(today())}, "name")
    if last_run:
        return
    low_stock = frappe.db.sql("""
    SELECT name, stock_qty, reorder_level
    FROM `tabSpare Part`
    WHERE stock_qty < reorder_level
    """, as_dict=True)

    html_template = """
        <h3>Low Stock Alert</h3>
        <p>The following spare parts are below reorder level:</p>

        <table border="1" cellpadding="6" cellspacing="0">
            <tr>
                <th>Part</th>
                <th>Stock Qty</th>
                <th>Reorder Level</th>
            </tr>

            {% for item in items %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.stock_qty }}</td>
                <td>{{ item.reorder_level }}</td>
            </tr>
            {% endfor %}
        </table>

        <br>
        <p>Please restock these items.</p>
        """

    message = frappe.render_template(html_template, {"items": low_stock})

    if low_stock:
        mail=frappe.get_single_value("QuickFix Settings",'manager_email')
        frappe.sendmail(recipients=[mail],subject="Low Stock Alert",message=message)

   




    
        


    
