import frappe
from frappe.utils import now_datetime, add_days,nowdate, add_months,now

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


@frappe.whitelist(allow_guest=True)
def cancel_old_draft_job_cards():
    start=time.time()
    frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE status = 'Draft
        ORDER BY creation ASC
        LIMIT 1000
    """)

    frappe.db.commit()
    end=time.time()
    print("Insert Time:", end - start)




@frappe.whitelist(allow_guest=True)
def bulk_insert():

    records = []

    for i in range(1000):
        records.append((
            frappe.generate_hash(),
            "Administrator",
            "bulk_cancel",
            now()
        ))

    frappe.db.bulk_insert(
        "Audit Log",
        ["name", "user", "action", "timestamp"],
        records,
        ignore_duplicates=False
    )

    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def get_job_summary():
    data=frappe.form_dict.get("Job")
    if data:
        print(data)
    else:
        # frappe.respnse("error": "Not found")
        print("HTTP 404,Not Found")
    doc=frappe.get_doc("Job Card",data)

    result = {
        "name": doc.name,
        "customer_name": doc.customer_name,
        "device_type": doc.device_type,
        "status": doc.status,
        "creation":doc.creation
    }
    return result

@frappe.whitelist(allow_guest=True)
def get_job_by_phone():
    ip = frappe.local.request_ip
    key = f"rate_limit:{ip}"

    count = frappe.cache().get(key) or 0
    if count >= 10:
        frappe.local.response["http_status_code"] = 429
        return {"error": "Too many requests"}

    frappe.cache().set_value(key, count + 1,60)
    return {"success": "Request allowed"}


@frappe.whitelist(allow_guest=True)
def get_status_chart_data():
    cache_key = "job_card_status_chart"

    data = frappe.cache.get_value(cache_key)


    if not data:
        frappe.log_error("yyyyy")
        data = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabJob Card`
            GROUP BY status
        """, as_dict=True)

        frappe.cache.set_value(cache_key, data, expires_in_sec=300)
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

    


###Get list:
# GET :http://quickfix-dev.localhost:8000/api/resource/Job_Card
### Single doc:
# GET :http://quickfix-dev.localhost:8000/api/resource/Job_Card

###create doc:
#POST : http://quickfix-dev.localhost:8000/api/resource/Spare Part

###update doc:
#PUT : http://quickfix-dev.localhost:8000/api/resource/Spare Part/None-'PART'-2026-0003
# {"unit_cost":50}

###DELETE doc:
#http://quickfix-dev.localhost:8000/api/resource/Spare Part/None-'PART'-2026-0003

