frappe.query_reports["Employee Idle Time Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "date_range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"reqd": 1
		}
	]
};