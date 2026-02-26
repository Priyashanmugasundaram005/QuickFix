import frappe


def send_urgent_alert(job_card,manager):
    frappe.sendmail(recipients=[manager],subject="Urgent Job Card Assigned",message=f"Job Card {job_card} is urgent and assign Technician")


def get_shop_name():
    return frappe.db.get_single_value("quickFix Settings",'shop_name')

def format_job_id(value):
    return f"JOB#{value}"