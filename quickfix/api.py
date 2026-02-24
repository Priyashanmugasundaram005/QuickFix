import frappe
from frappe.utils import now_datetime, add_days
from frappe.query_builder import DocType


@frappe.whitelist()
def get_overdue_jobs():
    JC = DocType("Job Card")
    seven_days_ago = add_days(now_datetime(), -7)

    overdue_jobs = (
        frappe.qb.from_(JC)
        .select(JC.name,JC.customer_name,JC.assigned_technician,JC.creation)
        .where(
            (JC.status.isin(["Pending Diagnosis", "In Repair"])) &
            (JC.creation < seven_days_ago)
        )
        .orderby(JC.creation)  
        .run(as_dict=True)
    )

    return overdue_jobs




@frappe.whitelist()
def transfer_job(from_tech, to_tech):
    try:
        frappe.db.sql(
            """
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
              AND status IN ('Pending Diagnosis', 'In Repair')
            """,
            (to_tech, from_tech),
        )
        frappe.db.commit()
        return "Success"

    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Job Transfer Failed")
        raise


@frappe.whitelist()
def share_job_card(job_card_name, user_email):
    frappe.share.add(
        doctype="Job Card",
        name=job_card_name,
        user=user_email,
        read=1,
        write=0,
        share=0
    )
    return "Job Card shared successfully"

@frappe.whitelist()
def manager_action():
    frappe.only_for("QF Manager")
    return "Successfully"