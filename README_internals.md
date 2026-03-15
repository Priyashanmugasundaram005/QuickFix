

## B2.Part A – Table Naming (Bench Console)

### 1. Tables matching `%Job%`

**Command**

```sql id="5c9d2f"
frappe.db.sql("SHOW TABLES LIKE '%Job%'")
```
**Output**

tabJob Card
tabScheduled Job Log
tabScheduled Job Type

**Explanation**

* Frappe stores each **DocType** as a table prefixed with `tab`.
* Format: `tab<DocType Name>`
* Example: `Job Card` → `tabJob Card`

---

### 2. Structure of `tabJob Card`

**Command**

```sql id="8b2d5a"
frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True)
```

### 3. Recognised columns

Common system fields:

* `name` – Primary key
* `creation` – Created timestamp
* `modified` – Last modified time
* `owner` – Document creator
* `docstatus` – Draft/Submitted/Cancelled status

These fields are automatically added by Frappe to manage documents.

## Part D – DocStatus Transitions

### 1. DocStatus values

* **0 – Draft** 
* **1 – Submitted** 
* **2 – Cancelled** 

### 2. Submitted & Cancelled behavior

* `doc.save()` on **Submitted** →  Not allowed (except fields with *Allow on Submit*).
* `doc.submit()` on **Cancelled** →  Not allowed. Must **Amend → Submit** to keep audit trail.


### 3. "Document has been modified after you opened it"

Occurs when:

* Another user/script updated the document.
* The `modified` timestamp changed.

**Purpose:** Prevents overwriting newer changes.

## Part E – Dangerous Patterns (Fix)

###  Issues

1. **`self.save()` inside `validate()`**

   * Causes recursion and breaks the document lifecycle.
   * `validate()` already runs during save.

2. **Unsafe update to another DocType**

   * Directly modifying Spare Part stock can cause data inconsistency.
   * No protection against concurrent updates.


###  Corrected approach

* Calculate totals inside `validate()` without calling `save()`.
* Update related documents within the same transaction so changes stay consistent.
* Ensure updates roll back automatically if the main document fails.


# Child Table Internals

## Auto-set Columns on Child Rows
When a row is added to `Job Card.parts_used` and saved, Frappe automatically sets:

- **parent** – Parent document name (Job Card ID)
- **parenttype** – Parent DocType ("Job Card")
- **parentfield** – Child table fieldname ("parts_used")
- **idx** – Row order in the table

---

## Child Table DB Name
The database table for **Part Usage Entry** DocType is:

tabPart Usage Entry

Frappe adds the `tab` prefix to all DocType tables.

---

## idx Behavior After Deletion
If the row at `idx = 2` is deleted and the document is saved:

- Remaining rows are automatically reordered.
- `idx` values are reset sequentially starting from 1.
- No gaps are left in row numbering.

---------------------------------------------------------------------------------------------------------------------------------------------------------

# Rename & Unique Constraints

## Rename Document
- After renaming a Technician, linked Job Cards **auto-update** the `assigned_technician` field.
- Frappe updates all Link fields to maintain referential integrity.
- Link fields store the document name (primary key), so references stay valid.

## Track Changes
- Records field-level changes in the Version log.
- Shows old value, new value, user, and timestamp.
- It does **not control link updates**.

## Unique Constraints

**Unique field in DocType**
- Enforced at database level.
- Prevents duplicates automatically.
- Reliable and fast.

**`frappe.db.exists()` in validate()**
- Enforced at application level.
- Can be bypassed in race conditions.
- Used for conditional uniqueness.

**Difference:** Database-level uniqueness is safer; validate() checks are for custom logic.

## Document Permissions Check

The output shows all permission values as 0, meaning the current user has no access to the Job Card. This happens when the user has no role permissions, is not the document owner, and the document has not been shared with them. The `frappe.get_doc_permissions(doc)` function returns the effective permissions for the logged-in user, which vary based on roles, ownership, and sharing settings.

## Recursion Pitfall in `on_update()` — Short Note

###  Wrong Pattern

```python
def on_update(self):
    self.save()  # causes infinite recursion
```

###  Why It’s Dangerous

`save()` triggers the document lifecycle again → `on_update()` runs repeatedly → infinite loop, timeouts, high CPU usage.

### Correct Pattern

Modify fields directly (no save needed):

```python
def on_update(self):
    self.status = "Updated"  #  safe
```

Or update DB without triggering hooks:

```python
frappe.db.set_value(self.doctype, self.name, "status", "Updated")
```

---------------------------------------------------------------------------------------------------------------------------------------------------------

## Part B — Upgrade Friction Analysis (Short)

###  Risk: Missing `super().validate()` in override_doctype_class

If Frappe adds new validations in `Job Card.validate()` and `super()` is not called:

* Core validations are skipped
* New framework checks won’t run
* Invalid data may be saved
* Upgrades can silently break business rules

---

###  Test to Catch This

Try inserting a Job Card that violates a core validation.

**Expected:** Insert fails
**If it succeeds:** `super().validate()` is missing and core logic is bypassed.

---

###  Why `doc_events` is Safer

* Preserves core logic
* Upgrade-friendly
* Multiple apps can hook safely
* No need to maintain `super()` chain

**override_doctype_class**

* Replaces core controller
* High upgrade risk
* Must maintain compatibility manually

**Rule:** Prefer `doc_events`; use override only when modifying core behavior is unavoidable.


## Part B – Multiple Validate Handlers

### Execution Order

When saving a **Job Card**, Frappe executes validate handlers in the following order:

1. **Controller `validate()` method**  
2. **`doc_events` handler for Job Card**  
3. **Wildcard `"*"` handler** (if defined)  

### If Both Handlers Raise `frappe.ValidationError`

- Execution stops at the first error.  
- Remaining handlers will **not** run.  
- Only **one error message** appears on the Desk.  

### `"*"` and Specific DocType Handler Together

- If both are registered for the same event:  
  - Both handlers run in sequence.  
  - **Specific DocType handler runs before wildcard**.  
  - If the first handler throws an error, the wildcard handler will **not** execute.

---------------------------------------------------------------------------------------------------------------------------------------------------------

# Part – Asset Hooks & Client Scripts (QuickFix)

## 1. app_include_js vs web_include_js

### app_include_js
Loads a JavaScript file only in the **Frappe Desk** (for logged-in users).

**Used for:**
- Internal UI tweaks
- Employee workflow helpers
- Desk notifications or shortcuts

### web_include_js
Loads a JavaScript file only on **Website/Portal pages**.

**Used for:**
- Customer portal enhancements
- Web form validation
- Public-facing UI interactions

---

## 2. DocType Client Scripts

### doctype_js (Job Card)
Runs only when the **Job Card form** is opened.

**Use cases:**
- Field validation
- Auto-calculations
- Dynamic field behavior

### doctype_list_js (Job Card)
Runs on the **Job Card list view**.

**Use cases:**
- Custom list buttons
- Row highlighting
- Bulk actions & filters

---

## 4. Build & Cache Busting

### What it does
- Compiles and bundles JS/CSS files
- Generates hashed filenames
- Updates asset manifest

### Why cache busting is needed
Browsers cache JS files. After changes, old files may still load.

Cache busting ensures:
- Latest JS is loaded
- Prevents stale scripts
- Avoids debugging issues

---

## 5. When to Run bench build
Run this command after:
- Modifying JS or CSS
- Adding asset hooks
- Updating client scripts
- Deploying to production

---------------------------------------------------------------------------------------------------------------------------------------------------------

## Override `frappe.client.get_count` – Internal Notes

### ✅ Tests

**1. Confirm override is called**

* Call: `frappe.client.get_count("Job Card")`
* Verify: New entry in **Audit Log** with action `count_queried`.

**2. Confirm original logic still works**

* Compare:

  * `frappe.client.get_count("Job Card")`
  * `frappe.db.count("Job Card")`
* Both counts must match.

**3. Confirm other apps are not broken**

* Any app calling `frappe.client.get_count` still receives correct count.
* No errors or behavior changes except logging.

---

### 🔁 override_whitelisted_methods vs Monkey Patching

| Feature     | Hook Override | Monkey Patching   |
| ----------- | ------------- | ----------------- |
| Mechanism   | hooks.py      | import-time code  |
| Visibility  | Explicit      | Hidden            |
| Safety      | Upgrade-safe  | Breaks on updates |
| Reversible  | Yes           | No                |
| Recommended | ✅ Yes        | ❌ Avoid          |

**When to use**

* Use **override_whitelisted_methods** for production-safe customization.
* Use monkey patching only for temporary debugging or experiments.


### ⚠️ Multiple Apps Overriding Same Method

If two apps override the same method:

* The app **last in apps.txt order wins**.
* Only one override runs.
* No automatic chaining.

---

### ⚠️ Signature Mismatch

Override must match original signature:

```python id="j6db9x"
get_count(doctype, filters=None, debug=False, cache=False)
```

If arguments differ, Frappe cannot map parameters → **TypeError**.

**Example Error**

TypeError: custom_get_count() missing required positional argument 'doctype'

**When it occurs**

* Missing parameters
* Different parameter order
* Extra required parameters


## Fieldname Collision Risk

When adding Custom Fields in Frappe, using a fieldname that may later be introduced by the core framework for the same DocType can lead to a **fieldname collision**.

### Effects
- Migration failure due to duplicate column creation
- Database schema conflicts
- Possible data loss
- UI inconsistencies or unexpected behavior

### Prevention
Use unique, app-prefixed fieldnames to avoid conflicts with future Frappe updates.

**Recommended pattern:**
- `qf_priority`
- `qf_service_status`
- `qf_internal_notes`

Using a prefix (e.g., `qf_` for QuickFix) ensures custom fields remain isolated from core changes.

---

## Patch Ordering & `patches.txt`

If Patch 1 creates a Custom Field and Patch 2 reads or updates it, they must be listed as **separate entries** in `patches.txt`.

### Why This Matters
- Patches run sequentially in the listed order
- Ensures the field exists before being accessed
- Allows safe resume if migration fails
- Simplifies debugging and rollback

### Best Practice
# patches.txt
quickfix.patches.v1_0.create_custom_fields
quickfix.patches.v1_0.update_custom_field_values

### Patch Safety – Quick Revision
_qf_patched Guard
Prevents a monkey patch from running multiple times during reloads.

**Without it**

Infinite recursion
Duplicate validations / DB writes
Performance issues
Unpredictable bugs

### Why monkey_patches.py (not __init__.py)?

Centralized, auditable patch location
Predictable execution
Easier debugging & disabling
Lower upgrade risk

### Escalation Order (Use in this order)

doc_events → safest, upgrade-friendly
override_doctype_class → controlled controller override
override_whitelisted_methods → alters API behavior
monkey patch → last resort, high risk

👉 Deeper override = higher fragility

### Monkey Patch Risks

Breaks after framework updates
Hidden side effects
Hard to maintain

### Client Validation & Async Calls — Quick Notes
❌ frappe.call inside validate (before_save)

Assertion: This pattern does not work reliably.

**Why?**

validate is synchronous.
frappe.call is asynchronous.
Form saves before the server response returns.
Errors thrown in callback cannot stop save.

**Result**

Race condition
Late error messages
Inconsistent data

Rule: Never use async calls to block save. Use server-side validation instead.

## Use Server-Side Validation (Recommended)

Server validation runs synchronously and reliably stops the save.

## Async Fetch → Use onload or refresh

Assertion: Async calls belong in onload or refresh, not in validate.

**Why?**
Runs after form loads
Safe for server calls
Does not interfere with save

**Use cases**
Fetch related data
Populate fields
Show alerts or indicators

## 🌳 Tree DocType – Quick Notes

A **Tree DocType** stores hierarchical data (parent → child) in an expandable tree.

### Examples
- Account → Chart of Accounts  
- Employee → Manager hierarchy  
- Item Group → Categories  

---

## doctype_tree_js

Used to add custom JS for **Tree View only**.

### hooks.py

```python
doctype_tree_js = {
    "Account": "public/js/account_tree.js"
}
```

**Uses**
Custom buttons
Expand/collapse control
Node UI customization

**How Tree Works**
Root nodes load first
Children load on expand
is_group shows expand icon

**Common Errors**
Missing is_group → no expand
Wrong parent field → broken hierarchy
Using list JS → no effect

---------------------------------------------------------------------------------------------------------------------------------------------------------

### Client Script DocType vs Shipped JS

**Client Script**
Created from Desk (stored in DB)
Used for quick UI changes
Not version controlled
Risky for large production apps

**Shipped JS (App Level)**
Stored inside custom app
Version controlled (Git)
Better for maintainable and scalable projects
Recommended for production

### Hiding Field vs Security
**Hiding with JS**
frm.set_df_property("customer_phone", "hidden", 1);
Only hides in UI
Data still accessible via API
Not secure

**Proper Security**
Use Role Permission Manager
Field-level permissions
Server-side validation (Python)

👉 Always enforce security on server side.

## Jinja Data Fetching Patterns in Frappe Print Formats

### 1. Using `frappe.get_all()` Directly in Jinja

You can fetch data directly inside the Jinja template using `frappe.get_all()`.

***Example:***

```jinja
{% set parts = frappe.get_all("Parts", filters={"job_card": doc.name}, fields=["part_name","quantity"]) %}

{% for part in parts %}
<tr>
<td>{{ part.part_name }}</td>
<td>{{ part.quantity }}</td>
</tr>
{% endfor %}
```



### Pre-compute Data in before_print() 

Instead of querying inside the template, fetch the required data in the controller using before_print() and attach it to the document.

***Controller Example***

def before_print(self):
    self.precomputed_parts = frappe.get_all(
        "Parts",
        filters={"job_card": self.name},
        fields=["part_name", "quantity"]
    )

**Template Usage**

{% for part in doc.precomputed_parts %}
<tr>
<td>{{ part.part_name }}</td>
<td>{{ part.quantity }}</td>
</tr>
{% endfor %}

---------------------------------------------------------------------------------------------------------------------------------------------------------

## Raw Printing vs HTML to PDF in Frappe

### 1. Raw Printing (ESC/POS)

Raw printing sends **printer control commands directly to the printer**.  
Thermal printers commonly use **ESC/POS commands**.

***Characteristics:***
- No HTML rendering
- No CSS support
- Direct communication with the printer
- Very fast and lightweight
- Typically used for **80mm receipt printers**

Example use case:
Retail stores printing **POS receipts** directly to a thermal printer.

---

### 2. HTML → PDF Rendering (WeasyPrint)

Frappe normally generates print formats as **HTML**, which are then converted to **PDF using WeasyPrint**.

***Process:***
1. Jinja template generates HTML
2. CSS styling is applied
3. WeasyPrint converts the HTML to a PDF document

***Characteristics:***
- Supports many HTML/CSS features
- Slower than raw printing
- Good for **invoices, job cards, reports**
- Produces high-quality printable documents

---

## CSS That Works in Browsers but Fails in WeasyPrint

Some CSS features supported by modern browsers do **not work correctly in WeasyPrint**.

***Examples:***

1. `position: sticky`
2. `flexbox gap property`
3. `backdrop-filter`

These may render correctly in Chrome but **fail or behave incorrectly in generated PDFs**.

---

## Thermal Print Format (80mm)

Thermal printers use **narrow paper widths**, typically **80mm**.  
The print format must be **minimal and compact**.

***Displayed fields:***
- Job Number
- Customer Name
- Total Amount

---

## Why Use format_value()

`format_value()` ensures numbers are displayed using the **correct currency and locale formatting**.

Example without formatting:

{{ doc.final_amount }}

Output might appear as:
2500

Example using formatting:

{{ format_value(doc.final_amount, "Currency") }}

Output becomes:
$ 2,500.00

***Benefits:***
- Correct currency symbol
- Proper decimal places
- Locale-aware formatting

---------------------------------------------------------------------------------------------------------------------------------------------------------
## Background Jobs: Queues

### short queue
Used for very quick tasks that finish within a few seconds.  
Examples: sending notifications, small updates, triggering lightweight events.

### default queue
Used for normal background tasks that take moderate time to complete.  
Examples: report generation, email sending, moderate data processing.

### long queue
Used for heavy or time-consuming operations.  
Examples: large data imports, backups, bulk updates, complex calculations.

### Why Multiple Queues?

Using separate queues ensures that **long-running tasks do not delay quick operations**, improving overall system performance and responsiveness.

### Disabling Scheduler for a Specific Site

The scheduler can be disabled for a site using the command:

bench --site sitename set-config pause_scheduler 1

### Why Disable Scheduler on a Dev Site?

On development sites, scheduled jobs may:
- Send unwanted emails or notifications
- Consume system resources
- Interfere with testing
Disabling the scheduler ensures that background jobs do not run automatically during development.

Explain retry behavior: how many times does Frappe retry a failed background job by
default?

If a background job fails, it will not retry automatically. The job is marked Failed immediately.



## N+1 Query Problem and Fix

### Problem
The code fetches all **Job Cards** and then runs another query for each **Technician** using `frappe.get_doc()`.  
This causes **N+1 queries** (1 query for Job Cards + N queries for Technicians), which reduces performance.

### Fix
Fetch data using a **single query with a join**.

```python
data = frappe.db.sql("""
SELECT jc.name, t.technician_name, t.phone
FROM `tabJob Card` jc
LEFT JOIN `tabTechnician` t
ON jc.assigned_technician = t.name
""", as_dict=True)
```

### Bulk operations

***Update***
Normal Update Time: 1.1649196147918701
Bulk Update Time: 0.003966093063354492

***Insert***
Normal Insert Time: 6.59688925743103
Bulk Insert Time: 0.09565520286560059

### Why Not Index Every Field?

Indexes speed up read queries, but they also have costs:

**Slower writes**: Insert, update, and delete operations become slower because indexes must also be updated.
**More storage usage**: Each index consumes additional database space.
**Maintenance overhead**: Too many indexes can reduce overall database performance.

Therefore,indexes should only be added to fields frequently used in filters, joins, or search operations.

---------------------------------------------------------------------------------------------------------------------------------------------------------

### Resource API

Get list:
GET :http://quickfix-dev.localhost:8000/api/resource/Job_Card
**Response**:
 "data": [
        {"name": "JC-2026-00002"},{"name": "JC-2026-00004"},{"name": "JC-2026-00012"},................]

Single doc:
GET :http://quickfix-dev.localhost:8000/api/resource/Spare Part/None-'PART'-2026-0003
**Response**:
"data": {
        "name": "None-'PART'-2026-0003",
        "owner": "Administrator",
        "creation": "2026-03-10 11:37:38.562906",
        "modified": "2026-03-10 11:37:38.562906",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "part_name": "Temper",
        "unit_cost": 30.0,
        "selling_price": 60.0,
        "stock_qty": 0.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    }

create doc:
POST : http://quickfix-dev.localhost:8000/api/resource/Spare Part
{"part_name":"Temper",
"selling_price":60,
"unit_cost":30}
**Response**:
    "data": {
        "name": "None-'PART'-2026-0003",
        "owner": "Administrator",
        "creation": "2026-03-10 11:37:38.562906",
        "modified": "2026-03-10 11:37:38.562906",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "part_name": "Temper",
        "unit_cost": 30.0,
        "selling_price": 60.0,
        "stock_qty": 0.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    },


Update doc:
PUT : http://quickfix-dev.localhost:8000/api/resource/Spare Part/None-'PART'-2026-0003
 {"unit_cost":50}
**Response**:"data": "ok"

DELETE doc:
http://quickfix-dev.localhost:8000/api/resource/Spare Part/None-'PART'-2026-0003
**Response**:"data": "ok"

## Return Type Serialization Result

**Result:**
When a Python `date` object is returned from a whitelisted method, Frappe automatically converts it into a JSON string in the API response.

Example JSON response:
{
  "message": "2026-03-10"
}

**Explanation:**
Frappe serializes Python objects like `date`, `datetime`, and `Decimal` into JSON-compatible formats. The Python `date` object is converted into an ISO formatted string (`YYYY-MM-DD`) before sending the response.


## Server Script Analysis

**Blocked Functions/Modules:** `os.system`, `subprocess`, `eval/exec`, `open()`

**Cannot Do in Server Script Can do in App Code**  
- Create/modify DocTypes  
- Import arbitrary Python modules  
- Run system-level commands  

**Acceptable Use Cases:**  
- Lightweight automation (e.g., send welcome email)  
- Quick validation or field updates  

**Require App Code:**  
- Complex multi-DocType logic  
- External integrations or heavy computation  

**Governance/Maintainability Risk:**  
- Hidden logic, no version control, performance/security issues

## Frappe Redis Cache

Frappe uses Redis to cache frequently accessed data to improve performance and reduce database queries.

❌frappe.cache.get_value("bootinfo")
✅frappe.cache.hget("bootinfo",frappe.session.user)

❌frappe.cache.get_value("quickfix:translations")  ---- As the key doesnt exist.
✅frappe.cache().hget("merged_translations","en")

### Common Data Cached in Redis

1. **Boot Info**
   - Contains information loaded during user login such as user details, roles, permissions, system defaults, and installed apps.
   - Used by the Desk UI to initialize the session.

2. **DocType Metadata (Meta)**
   - Stores the structure of DocTypes including fields, field types, permissions, and relationships.
   - Prevents repeated database queries when loading DocType definitions.

3. **Website Context**
   - Caches website-related data such as page context, templates, and configuration used for rendering web pages.

4. **Translations**
   - UI translation strings for different languages are cached (e.g., `merged_translations`).
   - Improves performance by avoiding repeated loading of translation files.

5. **User Permissions**
   - Stores role-based permissions and access control rules for users.
   - Helps quickly validate whether a user can access specific documents or actions.

### Benefit
Caching these items in Redis reduces database load and improves the overall performance of the Frappe framework.


## Stale UI Demonstration (Without Cache Invalidation)

Initially, the dashboard chart used cached Job Card status data. After changing a Job Card status, the chart still showed **old data** because the cache was not cleared.

After adding cache invalidation in the **on_update** event, the cache is cleared and the dashboard now shows the **updated data correctly**.

## Debugging Stale UI

- **Old JS after changes:** Run `bench build --app quickfix` to rebuild frontend assets and clear the asset cache so the browser loads the updated JS.

- **Role of bench build:** It compiles and bundles the app’s JS/CSS files and updates the built assets used by the browser.

- **Old DocType field labels:** Run `bench migrate` or `bench clear-cache` to clear the **DocType metadata cache** so users see the updated fields.

### Webhook

## Security

**Why use `hmac.compare_digest()`?**  
`hmac.compare_digest()` prevents **timing attacks**.  
Unlike normal `==` comparison, it performs a **constant-time comparison**, ensuring secure signature validation.

## Deduplication Strategy

Each webhook event is recorded in the **Audit Log** using the Job Card reference.  
If the same event is received again, the system detects the existing log entry and returns **"duplicate"** without processing it again.

---------------------------------------------------------------------------------------------------------------------------------------------------------
###Places Using ignore_permissions=True

1. Location:api.py - payment_webhook() – job.save(ignore_permissions=True)
Justification: The payment webhook is a system-triggered action from a payment gateway, so the backend must update the Job Card payment status even though no logged-in user is performing the action.

2. Location:api.py - payment_webhook() – Audit Log.insert(ignore_permissions=True)
Justification: The system automatically creates an audit log entry for tracking payment events, so permission checks are bypassed because it is a backend system record.

3. Location:custom_job_card.py - create_audit_log() – audit.insert(ignore_permissions=True)
Justification: Audit logs are generated by backend processes or scheduled jobs, so permissions are bypassed to ensure logging always succeeds.

4. Location:custom_job_card.py - install() – device.insert(ignore_permissions=True)
Justification: Device Type records are created during the app installation process, which is a system setup task.

5. Location:custom_job_card.py - install() – settings.save(ignore_permissions=True)
Justification: Default values for QuickFix Settings are configured automatically during installation by the system.

6. Location:job_card.py - on_submit() – new_ent.insert(ignore_permissions=True)
Justification: A Service Invoice is generated automatically when a Job Card is submitted.

7. Location:audit_log.py - log_in() – Audit Log.insert(ignore_permissions=True)
Justification: The system automatically logs user login events for auditing purposes.

8. Location:audit_log.py - log_out() – Audit Log.insert(ignore_permissions=True)
Justification: The system automatically logs user logout events to maintain activity tracking.

### Malicious Scenario

If a malicious intern adds ignore_permissions=True to a @frappe.whitelist(allow_guest=True) endpoint, any unauthenticated user could bypass permission checks and read or modify restricted data, leading to serious security vulnerabilities such as unauthorized data access or record manipulation.