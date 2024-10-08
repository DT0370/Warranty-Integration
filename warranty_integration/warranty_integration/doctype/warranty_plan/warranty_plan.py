# Copyright (c) 2024, DTeam and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from datetime import datetime
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 


class WarrantyPlan(Document):
	def on_submit(self):
		warranty_settings = frappe.get_doc('Extended Warranty Integration Settings')
		headers = {
            warranty_settings.api_key: warranty_settings.api_secret
		}
		body = {
			"action": "CREATE WARRANTY PLAN",
		}
		sample_date = datetime.now()

		body.update(
			{
				"FirstName":self.customer_name,
				"LastName":"test",
				"CustomerEmail": self.customer_email,
				"CustomerPhone": self.customer_phone,
				"address": self.address_display,
				"State":self.state,
				"Model":self.item_code,
				"SerialNumber":self.serial_no,
				"Plan":self.warranty_plan_type,
				"InvoiceDate": self.purchase_date.isoformat() if type(self.purchase_date) == type(sample_date.date()) else datetime.strptime(self.purchase_date, "%Y-%m-%d").isoformat(),
				"InstallationDate": self.installation_date.isoformat() if type(self.installation_date) == type(sample_date.date()) else datetime.strptime(self.installation_date, "%Y-%m-%d").isoformat(),
				"TVLandingCost": str(self.tv_landing_cost)
			}
		)
 		# Make the POST request
		webhook_log = frappe.new_doc("Extended Warranty Request Log")
		webhook_log.request_for = "CREATE WARRANTY CLAIM"
		webhook_log.reference_document = self.name
		webhook_log.headers = str(headers)
		webhook_log.data = str(json.dumps(body))
		webhook_log.user = self.modified_by
		webhook_log.url = warranty_settings.base_url
		try:
			response = requests.post(warranty_settings.base_url,headers=headers,data=json.dumps(body))
			webhook_log.response = response
			webhook_log.message = str(response.json())
			
		except HTTPError as http_err:
			webhook_log.error = http_err
			frappe.throw(_("HTTP Error {0}".format(http_err)))
		update_warranty_plan(self,response.json())
		webhook_log.insert()

@frappe.whitelist(allow_guest=True)
def update_warranty_plan(self,data):
	self.warranty_start_date = datetime.strptime(data.get("Warranty Start Date"), "%d-%m-%Y")
	self.warranty_end_date = datetime.strptime(data.get("Warranty End Date"), "%d-%m-%Y")
	self.warranty_id = data.get("Warranty Id")
	self.save()
	self.reload()