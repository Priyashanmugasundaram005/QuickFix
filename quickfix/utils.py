import frappe


def send_urgent_alert(job_card,manager):
    frappe.sendmail(recipients=[manager],subject="Urgent Job Card Assigned",message=f"Job Card {job_card} is urgent and assign Technician")