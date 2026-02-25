from quickfix.service_center.doctype.job_card.job_card import JobCard
import frappe

class CustomJobCard(JobCard):
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