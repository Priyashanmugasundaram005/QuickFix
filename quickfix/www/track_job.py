import frappe

def get_context(context):
    print("context---------")
    context.title = "Track Job Status"
    context.description = "Track your device repair job status"
    context.og_title = "Track Job - QuickFix"

    job_card = frappe.form_dict.get("job_card")

    if job_card:
        job = frappe.db.get_value(
            "Job Card",
            job_card,
            ["name", "status", "device", "technician", "final_amount"],
            as_dict=True
        )

        context.job = job