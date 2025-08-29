import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Item Amount"), "fieldname": "item_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Distributed Tip"), "fieldname": "distributed_tip", "fieldtype": "Currency", "width": 120},
        {"label": _("Base Commission"), "fieldname": "base_commission", "fieldtype": "Currency", "width": 120},
        {"label": _("Tip Commission"), "fieldname": "tip_commission", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Commission"), "fieldname": "total_commission", "fieldtype": "Currency", "width": 130},
    ]

def get_data(filters):
    conditions = ""
    if filters.get("employee"):
        conditions += f" AND sii.sales_person = '{filters.get('employee')}'"
    
    si_doctype = frappe.qb.DocType("Sales Invoice")
    sii_doctype = frappe.qb.DocType("Sales Invoice Item")

    total_tips_query = (frappe.qb.from_(si_doctype)
        .select(si_doctype.name, si_doctype.custom_tips_amount, si_doctype.net_total)
        .where((si_doctype.docstatus == 1) & (si_doctype.is_return == 0))
    ).as_("tips_data")

    query = (
        frappe.qb.from_(sii_doctype)
        .inner_join(si_doctype)
        .on(sii_doctype.parent == si_doctype.name)
        .left_join(total_tips_query)
        .on(si_doctype.name == total_tips_query.name)
        .select(
            si_doctype.posting_date,
            si_doctype.name.as_("sales_invoice"),
            si_doctype.customer,
            sii_doctype.item_name,
            sii_doctype.amount.as_("item_amount"),
            sii_doctype.base_commission_amount.as_("base_commission"),
            sii_doctype.tip_commission_amount.as_("tip_commission"),
            sii_doctype.total_commission
        )
        .where(
            (si_doctype.docstatus == 1)
            & (sii_doctype.sales_person.isnotnull())
            & (si_doctype.posting_date.between(filters.get("from_date"), filters.get("to_date")))
        )
    )

    if filters.get("employee"):
        query = query.where(sii_doctype.sales_person == filters.get("employee"))

    data = query.run(as_dict=True)

    # Calculate distributed tip for display purposes
    # Note: This is a simplified display calculation. The actual commission is already stored.
    inv_totals = {}
    for row in data:
        if row.sales_invoice not in inv_totals:
            doc = frappe.get_doc("Sales Invoice", row.sales_invoice)
            inv_totals[row.sales_invoice] = {
                "tips": doc.custom_tips_amount, 
                "total_amt": sum(d.amount for d in doc.items)
            }
        
        totals = inv_totals[row.sales_invoice]
        if totals.get("total_amt"):
            proportion = row.item_amount / totals["total_amt"]
            row.distributed_tip = totals["tips"] * proportion
        else:
            row.distributed_tip = 0
    
    return data