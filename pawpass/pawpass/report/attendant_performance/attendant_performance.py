# Copyright (c) 2026, Santhiya and contributors
# For license information, please see license.txt

import frappe
from frappe import _


# def execute(filters: dict | None = None):
# 	"""Return columns and data for the report.

# 	This is the main entry point for the report. It accepts the filters as a
# 	dictionary and should return columns and data. It is called by the framework
# 	every time the report is refreshed or a filter is updated.
# 	"""
# 	columns = get_columns()
# 	data = get_data()

# 	return columns, data

# def execute_snapshot_report(filters: dict | None = None):
# 	"""Return columns and data for the report.

# 	This is the main entry point for snapshot report. When 'Synced
# 	Report' is enabled in report, framework will call this method
# 	every time the report is refreshed or a filter is updated. It
# 	accepts the same filters as normal execute. But a utility method -
# 	get_latest_sync, is also imported.

# 	"""
# 	from frappe.database.duckdb.database import get_latest_sync

# 	columns = get_columns()
# 	data = get_data()

# 	return columns, data

# def get_columns() -> list[dict]:
# 	"""Return columns for the report.

# 	One field definition per column, just like a DocType field definition.
# 	"""
# 	return [
# 		{
# 			"label": _("Column 1"),
# 			"fieldname": "column_1",
# 			"fieldtype": "Data",
# 		},
# 		{
# 			"label": _("Column 2"),
# 			"fieldname": "column_2",
# 			"fieldtype": "Int",
# 		},
# 	]


# def get_data() -> list[list]:
# 	"""Return data for the report.

# 	The report data is a list of rows, with each row being a list of cell values.
# 	"""
# 	return [
# 		["Row 1", 1],
# 		["Row 2", 2],
# 	]

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns,data

def get_columns():
	return [
		{
			"label":_("Attendant"),
			"fieldname":"assigned_attendant",
			"fieldtype":"Link",
			"options":"ATTENDANT"
		},
		{
			"label":_("Total Stays"),
			"fieldname":"total_stays",
			"fieldtype":"Int"
		},
		{
			"label":_("Completed"),
			"fieldname":"completed_stays",
			"fieldtype":"Int"
		},
		{
			"label":_("Average Stay Length (nights)"),
			"fieldname":"average_stay_length",
			"fieldtype":"Int"
			
		},
		{
			"label":_("Revenue"),
			"fieldname":"revenue",
			"fieldtype":"Currency",
			"width": 150
		},
		{
			"label":_("Completion Rate %"),
			"fieldname":"completion_rate",
			"fieldtype":"Percent"
		}
	]

def get_data(filters=None):
	fiters = filters or {}

	query = """select assigned_attendant, count(name) as total_stays,sum(case when status='Picked Up' then 1 else 0 end) as completed_stays, round(avg(datediff(checkin_date,actual_checkout_date)),0) as average_stay_length, sum(case when status='Picked Up' then final_amount else 0 end) as revenue, round((sum(case when status='Picked Up' then 1 else 0 end)/count(name))*100,2) as completion_rate from `tabStay Card` group by assigned_attendant order by assigned_attendant asc"""

	return frappe.db.sql(query,filters,as_dict=True)

