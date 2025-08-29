import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

print("<<<<<<<<<< HELLO, I AM THE INSTALL.PY SCRIPT AND I AM RUNNING! >>>>>>>>>>")

def after_install():
    # ... (this part is correct)
    print("Starting AntPOS Salon setup...")
    create_salon_custom_fields()
    company = get_default_company()
    if company:
        create_required_accounts(company)
        setup_tips_in_tax_template(company)
    else:
        print("Warning: No default company found. Skipping Account and Tax Template setup.")
    print("AntPOS Salon setup completed successfully.")

def create_salon_custom_fields():
    # ... (this part is correct)
    print("Creating custom fields...")
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "custom_tips_amount"}):
        create_custom_field("Sales Invoice", {"fieldname": "custom_tips_amount", "label": "Tips Amount", "fieldtype": "Currency", "insert_after": "grand_total"})
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice Item", "fieldname": "sales_person"}):
        create_custom_field("Sales Invoice Item", {"fieldname": "sales_person", "label": "Sales Person", "fieldtype": "Link", "options": "Employee", "insert_after": "item_name"})
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice Item", "fieldname": "commission_rate"}):
        create_custom_field("Sales Invoice Item", {"fieldname": "commission_rate", "label": "Commission Rate (%)", "fieldtype": "Float", "default": "40.0", "insert_after": "amount"})
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice Item", "fieldname": "base_commission_amount"}):
        create_custom_field("Sales Invoice Item", {"fieldname": "base_commission_amount", "label": "Base Commission", "fieldtype": "Currency", "read_only": 1, "insert_after": "commission_rate"})
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice Item", "fieldname": "tip_commission_amount"}):
        create_custom_field("Sales Invoice Item", {"fieldname": "tip_commission_amount", "label": "Tip Commission", "fieldtype": "Currency", "read_only": 1, "insert_after": "base_commission_amount"})
    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice Item", "fieldname": "total_commission"}):
        create_custom_field("Sales Invoice Item", {"fieldname": "total_commission", "label": "Total Commission", "fieldtype": "Currency", "read_only": 1, "options": "base_commission_amount + tip_commission_amount", "insert_after": "tip_commission_amount"})
    print("Custom fields created.")

def create_required_accounts(company):
    # ... (this part is correct)
    print(f"Creating accounts for company: {company}...")
    income_parent = frappe.db.get_value("Account", {"company": company, "account_name": ["in", ["Direct Income", "Direct Revenue"]], "is_group": 1})
    if not income_parent:
        income_parent = frappe.db.get_value("Account", {"company": company, "root_type": "Income", "is_group": 1})
    liability_parent = frappe.db.get_value("Account", {"company": company, "account_name": "Current Liabilities", "is_group": 1})
    if not liability_parent:
        liability_parent = frappe.db.get_value("Account", {"company": company, "root_type": "Liability", "is_group": 1})

    if not income_parent or not liability_parent:
        print("ERROR: Could not find suitable parent Income/Liability accounts.")
        return

    tips_account_name = "Tips Received"
    if not frappe.db.exists("Account", {"account_name": tips_account_name, "company": company}):
        frappe.get_doc({"doctype": "Account", "account_name": tips_account_name, "parent_account": income_parent, "company": company, "account_type": "Income Account"}).insert(ignore_permissions=True)
        print(f"Created Account: '{tips_account_name}' under '{income_parent}'")

    commission_account_name = "Employee Commissions Payable"
    if not frappe.db.exists("Account", {"account_name": commission_account_name, "company": company}):
        frappe.get_doc({"doctype": "Account", "account_name": commission_account_name, "parent_account": liability_parent, "company": company, "account_type": "Payable"}).insert(ignore_permissions=True)
        print(f"Created Account: '{commission_account_name}' under '{liability_parent}'")

    frappe.db.commit()
    print("Account creation/verification complete.")

def setup_tips_in_tax_template(company):
    print("Setting up 'Tips' in Sales Taxes and Charges Template...")
    company_abbr = frappe.get_cached_value('Company', company, 'abbr')
    
    # ================== THE CRITICAL FIX ==================
    # Construct the full, correct account name that ERPNext expects.
    # It might be "Tips Received" or "Tips Received - ABBR" depending on settings.
    # We query for it to be 100% sure.
    tips_account_full_name = frappe.db.get_value("Account", {"account_name": "Tips Received", "company": company})
    if not tips_account_full_name:
        print("ERROR: 'Tips Received' account not found after creation. Aborting tax setup.")
        return
    # ======================================================

    template_name = frappe.db.get_value("Sales Taxes and Charges Template", {"is_default": 1, "company": company})
    
    if not template_name:
        template_name = f"POS Charges - {company_abbr}"
        if not frappe.db.exists("Sales Taxes and Charges Template", template_name):
             frappe.get_doc({
                "doctype": "Sales Taxes and Charges Template",
                "title": template_name,
                "company": company,
                "is_default": 1,
                "taxes": []
             }).insert(ignore_permissions=True)
             frappe.db.commit()
             print(f"Created default template: {template_name}")
    
    template_doc = frappe.get_doc("Sales Taxes and Charges Template", template_name)
    if not any(tax.description == "Tips" for tax in template_doc.taxes):
        template_doc.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": tips_account_full_name, # Use the full, correct name
            "description": "Tips",
            "cost_center": frappe.get_cached_value('Company', company, 'cost_center'),
            "rate": 0,
        })
        template_doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Added 'Tips' charge to template: {template_name}")
    else:
        print("'Tips' charge already exists in template.")

def get_default_company():
    # ... (this part is correct)
    company = frappe.get_single("Global Defaults").default_company
    if not company:
        companies = frappe.get_all("Company", limit=1)
        if companies:
            company = companies[0].name
    return company