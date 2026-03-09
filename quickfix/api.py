import frappe
from frappe.utils import now_datetime, add_days,nowdate, add_months

from datetime import datetime
from frappe.query_builder import DocType
from frappe.client import get_count
from quickfix.overrides.custom_job_card import create_audit_log

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




@frappe.whitelist(allow_guest=True)
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    # Log API usage
    # frappe.msgprint("Override is running")
    print("doneeeeeeeee")
    create_audit_log(doctype_name=doctype, action="count_queried")
    # todo = frappe.get_doc({"doctype":"ToDo", "description": "test"})
    # print(todo)
    # todo.insert(ignore_permissions=True)
    # print(todo)
    # frappe.db.commit()
    print("11111111111111111111")
    

    # Call original behavior
    return get_count(doctype, filters, debug, cache)




@frappe.whitelist()
def get_shop_name():
    return frappe.db.get_single_value("QuickFix Settings", "shop_name")


def monthly_revenue():

    revenue = frappe.db.sql("""
        SELECT SUM(final_amount) as revenue
        FROM `tabJob Card`
        WHERE status='Delivered'
        AND MONTH(delivery_date) = MONTH(CURDATE() - INTERVAL 1 MONTH)
    """, as_dict=True)[0].revenue or 0

    manager = frappe.get_single_value("QuickFix Settings", "manager_email")

    html_template = """
    <h2>Monthly Revenue Report</h2>

    <p>The revenue for the previous month is:</p>

    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Month</th>
            <th>Total Revenue</th>
        </tr>

        <tr>
            <td>{{ month }}</td>
            <td>{{ revenue }}</td>
        </tr>
    </table>

    <br>
    <p>This report was generated automatically by QuickFix.</p>
    """

    prev_month = datetime.strptime(add_months(nowdate(), -1), "%Y-%m-%d").strftime("%B %Y")


    message = frappe.render_template(
        html_template,
        {
            "month": prev_month,
            "revenue": revenue
        }
    )

    frappe.sendmail(
        recipients=[manager],
        subject="Monthly Revenue Report",
        message=message
    )
