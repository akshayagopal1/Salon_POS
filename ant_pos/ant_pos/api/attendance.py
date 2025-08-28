import frappe
from frappe import _

@frappe.whitelist()
def get_employees():
    """
    Fetch all active employees for dropdown selection.
    Returns a list of dicts with 'label' and 'value'.
    """
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name"],
        order_by="employee_name asc",
    )

    options = [{"label": emp["employee_name"], "value": emp["name"]} for emp in employees]
    return options

@frappe.whitelist()
def get_dropdown_data():
    """
    Fetch all dropdown data for attendance form.
    Returns employees, companies, and shifts.
    """
    # Get employees
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name"],
        order_by="employee_name asc",
    )

    # Get companies
    companies = frappe.get_all(
        "Company",
        fields=["name"],
        order_by="name asc",
    )

    # Get shifts
    shifts = frappe.get_all(
        "Shift Type",
        fields=["name"],
        order_by="name asc",
    )

    return {
        "employees": employees,
        "companies": companies,
        "shifts": shifts
    }


@frappe.whitelist()
def create_attendance(values):
    """
    Create a new Attendance record.

    Args:
        values (dict): Should include mandatory fields:
            - employee
            - status
            - attendance_date
            - company
        Optional fields:
            - shift
            - late_entry
            - early_exit

    Returns:
        str: Name of the created Attendance document.
    """
    try:
        if isinstance(values, str):
            import json
            values = json.loads(values)
            
        # Validate required fields
        required_fields = ['employee', 'status', 'attendance_date']
        for field in required_fields:
            if not values.get(field):
                frappe.throw(_(f"Missing required field: {field}"))
        
        # Fetch company from Employee
        company = frappe.db.get_value("Employee", values.get("employee"), "company")
        if not company:
            frappe.throw(_("Selected employee does not have a company assigned"))

        # Create Attendance document
        attendance = frappe.new_doc("Attendance")
        
        # Set mandatory fields
        attendance.employee = values.get('employee')
        attendance.status = values.get('status')
        attendance.attendance_date = values.get('attendance_date')
        attendance.company = company  # Must set company here
        
        # Set optional fields if provided
        if values.get('shift'):
            attendance.shift = values.get('shift')
        if 'late_entry' in values:
            attendance.late_entry = 1 if values.get('late_entry') > 0 else 0
        if 'early_exit' in values:
            attendance.early_exit = 1 if values.get('early_exit') > 0 else 0

        # Insert and submit
        attendance.insert()
        attendance.submit()

        return attendance.name

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Attendance Creation Error")
        frappe.throw(str(e))
