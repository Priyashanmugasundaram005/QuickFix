app_name = "quickfix"
app_title = "quickfix"
app_publisher = "priii"
app_description = "quickfix"
app_email = "yashinishan2005@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "quickfix",
# 		"logo": "/assets/quickfix/logo.png",
# 		"title": "quickfix",
# 		"route": "/quickfix",
# 		"has_permission": "quickfix.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/quickfix/css/quickfix.css"
app_include_js = "/assets/quickfix/js/quickfix.js"

# website_route_rules=[{"form_route":"/track-job","to_route":"track-job"}]

# include js, css files in header of web template
# web_include_css = "/assets/quickfix/css/quickfix.css"
# web_include_js = "/assets/quickfix/js/quickfix.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "quickfix/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "quickfix/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": "quickfix.utils.get_shop_name",
	"filters": "quickfix.utils.format_job_id"
}

# Installation
# ------------

extend_bootinfo = "quickfix.overrides.custom_job_card.extend_bootinfo"

# before_install = "quickfix.install.before_install"
after_install = "quickfix.overrides.custom_job_card.install"

# Uninstallation
# ------------

before_uninstall = "quickfix.overrides.custom_job_card.before_install"
# after_uninstall = "quickfix.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "quickfix.utils.before_app_install"
# after_app_install = "quickfix.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "quickfix.utils.before_app_uninstall"
# after_app_uninstall = "quickfix.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "quickfix.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Job Card": "quickfix.service_center.doctype.job_card.job_card.permission_query_conditions",
}

has_permission = {
	"Job Card": "quickfix.service_center.doctype.service_invoice.service_invoice.has_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Job Card": "quickfix.overrides.custom_job_card.CustomJobCard"
}

on_session_creation=['quickfix.service_center.doctype.audit_log.audit_log.log_in']

on_logout="quickfix.service_center.doctype.audit_log.audit_log.log_out"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_update": "quickfix.overrides.custom_job_card.log",
        "on_submit":"quickfix.overrides.custom_job_card.log",
        "on_save":"quickfix.overrides.custom_job_card.log",
		"on_cancel": "quickfix.overrides.custom_job_card.log",
		"on_trash": "quickfix.overrides.custom_job_card.log"
	 },
    "Job Card":{
        "validate":"quickfix.overrides.custom_job_card.validate_job_card"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"quickfix.tasks.all"
# 	],
# 	"daily": [
# 		"quickfix.tasks.daily"
# 	],
# 	"hourly": [
# 		"quickfix.tasks.hourly"
# 	],
# 	"weekly": [
# 		"quickfix.tasks.weekly"
# 	],
# 	"monthly": [
# 		"quickfix.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "quickfix.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.client.get_count": "quickfix.api.custom_get_count"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "quickfix.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["quickfix.utils.before_request"]
# after_request = ["quickfix.utils.after_request"]

# Job Events
# ----------
# before_job = ["quickfix.utils.before_job"]
# after_job = ["quickfix.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

fixtures=[
    # "Role",
    {
    'dt':'DocPerm',
    filter:['parent', 'in', ['Device Type','Technician','Spare Part','Job Card','Service Invoice']]
    },
    {
        'dt':'Role',
        filter:['parent','in',['QF Manager','QF Technician','QF Service Staff']]
        
    }, 
    


    
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"quickfix.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

