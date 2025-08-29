import frappe
from frappe import _
from frappe.utils import get_datetime

def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": _("End of Service"), "fieldname": "end_of_service", "fieldtype": "Datetime", "width": 200},
        {"label": _("Start of Next Service"), "fieldname": "start_of_next_service", "fieldtype": "Datetime", "width": 200},
        {"label": _("Idle Time (minutes)"), "fieldname": "idle_time_minutes", "fieldtype": "Float", "width": 150},
    ]

def get_data(filters):
    if not filters.get("date_range"):
        return []

    from_date, to_date = filters.get("date_range")
    
    conditions = "WHERE `timestamp` BETWEEN %(from_date)s AND %(to_date)s"
    values = {"from_date": from_date + " 00:00:00", "to_date": to_date + " 23:59:59"}

    if filters.get("employee"):
        conditions += " AND `employee` = %(employee)s"
        values["employee"] = filters.get("employee")
        
    # Using Frappe's new QB for MariaDB/PostgreSQL compatibility
    eal = frappe.qb.DocType("Employee Activity Log")
    log_data = (
        frappe.qb.from_(eal)
        .select(eal.employee, eal.activity_type, eal.timestamp)
        .where(eal.timestamp.between(values["from_date"], values["to_date"]))
        .orderby(eal.employee, eal.timestamp)
    )
    if filters.get("employee"):
        log_data = log_data.where(eal.employee == filters.get("employee"))

    logs = log_data.run(as_dict=True)

    # Process logs to find idle time
    result = []
    employee_logs = {}
    for log in logs:
        if log.employee not in employee_logs:
            employee_logs[log.employee] = []
        employee_logs[log.employee].append(log)

    for employee, logs in employee_logs.items():
        for i in range(len(logs) - 1):
            current_log = logs[i]
            next_log = logs[i+1]

            if current_log.activity_type == "Service Completed" and next_log.activity_type == "Service Started":
                end_time = get_datetime(current_log.timestamp)
                start_time = get_datetime(next_log.timestamp)
                
                idle_seconds = (start_time - end_time).total_seconds()
                idle_minutes = round(idle_seconds / 60, 2)
                
                # Only show meaningful idle times
                if idle_minutes > 0:
                    result.append({
                        "employee": employee,
                        "end_of_service": end_time,
                        "start_of_next_service": start_time,
                        "idle_time_minutes": idle_minutes,
                    })

    return result