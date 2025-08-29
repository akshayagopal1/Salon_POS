# In payment_entry.py

import frappe
from frappe.utils import flt

@frappe.whitelist()
def settle_invoices_with_payment(customer, references, payments, pos_profile):
    """
    Creates one or more Payment Entries to settle outstanding invoices.
    This is a transactional and more robust way to handle payment allocation.
    """
    if not customer or not references or not payments:
        frappe.throw("Customer, References, and Payment details are required.")

    # Get required accounts from POS Profile and Company
    profile = frappe.get_doc("POS Profile", pos_profile)
    company_doc = frappe.get_doc("Company", profile.company)
    debtors_account = company_doc.default_receivable_account

    if not debtors_account:
        frappe.throw("Default Receivable Account is not set in Company defaults.")

    selected_invoices = frappe.get_all("Sales Invoice", 
        filters={'name': ('in', references)}, 
        fields=['name', 'outstanding_amount']
    )
    
    # Sort invoices to pay off oldest ones first if needed (optional)
    selected_invoices = sorted(selected_invoices, key=lambda i: i.name)

    for payment in payments:
        mode_of_payment = payment.get("mode_of_payment")
        amount_to_allocate = flt(payment.get("amount"))

        # Find the default account for this mode of payment from the POS Profile
        paid_to_account = None
        for p in profile.payments:
            if p.mode_of_payment == mode_of_payment:
                paid_to_account = p.default_account
                break
        
        if not paid_to_account:
            frappe.throw(f"Default Account for Mode of Payment '{mode_of_payment}' not found in POS Profile '{pos_profile}'.")

        if amount_to_allocate <= 0:
            continue

        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.party_type = "Customer"
        pe.party = customer
        pe.posting_date = frappe.utils.today()
        pe.mode_of_payment = mode_of_payment
        pe.paid_from = debtors_account
        pe.paid_to = paid_to_account
        
        pe.paid_amount = amount_to_allocate
        pe.received_amount = amount_to_allocate

        # Allocate the amount across the selected invoices
        for inv in selected_invoices:
            if amount_to_allocate <= 0:
                break
            
            if flt(inv.outstanding_amount) > 0:
                allocated = min(amount_to_allocate, flt(inv.outstanding_amount))
                pe.append("references", {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": inv.name,
                    "allocated_amount": allocated,
                })
                # Reduce outstanding amount for next payment mode in this run
                inv.outstanding_amount -= allocated
                amount_to_allocate -= allocated
        
        pe.save()
        pe.submit()

    return {"status": "success", "message": "Payments created successfully."}