import frappe
from frappe.utils import flt

@frappe.whitelist()
def calculate_commission_on_validate(doc, method):
    if doc.is_return or doc.docstatus != 0:
        return

    logged_employees = set()
    total_tips = flt(doc.get("custom_tips_amount"))
    net_total_for_tips = sum(flt(item.rate) * flt(item.qty) for item in doc.items)

    for item in doc.items:
        commission_rate = flt(item.get("commission_rate"))
        base_amount = flt(item.rate) * flt(item.qty)
        item.base_commission_amount = (base_amount * commission_rate) / 100

        tip_commission = 0
        if total_tips > 0 and net_total_for_tips > 0:
            item_proportion = base_amount / net_total_for_tips
            distributed_tip_for_item = total_tips * item_proportion
            tip_commission = (distributed_tip_for_item * commission_rate) / 100
        item.tip_commission_amount = tip_commission
        
        sales_person = item.get("sales_person")
        if sales_person and sales_person not in logged_employees:
            create_activity_log(sales_person, "Service Started", doc.name)
            logged_employees.add(sales_person)

@frappe.whitelist()
def log_activity_on_submit(doc, method):
    if doc.is_return:
        return

    logged_employees = set()
    for item in doc.items:
        sales_person = item.get("sales_person")
        if sales_person and sales_person not in logged_employees:
            create_activity_log(sales_person, "Service Completed", doc.name)
            logged_employees.add(sales_person)

def create_activity_log(employee, activity_type, sales_invoice):
    if activity_type == "Service Started":
        if frappe.db.exists("Employee Activity Log", {"sales_invoice": sales_invoice, "employee": employee, "activity_type": "Service Started"}):
            return

    try:
        log = frappe.new_doc("Employee Activity Log")
        log.employee = employee
        log.activity_type = activity_type
        log.sales_invoice = sales_invoice
        log.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to create Employee Activity Log for {employee}", str(e))