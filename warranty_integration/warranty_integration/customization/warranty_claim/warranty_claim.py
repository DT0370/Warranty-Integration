import frappe
from frappe import _
import datetime
from datetime import datetime
import json
import re
import requests, json
from requests.exceptions import HTTPError 

def validate(doc,method=None):
    warranty_settings = frappe.get_doc('Extended Warranty Integration Settings')
    headers = {
        warranty_settings.api_key_claim: warranty_settings.api_secret_claim
    }
    body = {
        "action": "CREATE WARRANTY CLAIM",
    }
    body ={
        "PolicyNo": doc.custom_policy_no,
        "Status": doc.status,
        "IncidentNumber": doc.name,
        "FirstName": doc.customer_name,
        "LastName":"",
        "CustomerEmail":doc.contact_email,
        "CustomerPhone":doc.contact_mobile,
        "address":doc.service_address or doc.address_display,
        "State":doc.custom_state,
        "Landmark":doc.custom_landmark,
        "Model":doc.item_code,
        "SerialNumber":doc.serial_no,
        "Issue":doc.complaint,
        "EWEndDate": doc.custom_ew_end_date.isoformat(),
        "Level1TroubleshootingDetails":doc.custom_level1_troubleshooting_details,
        "Level2TroubleshootingDetails":doc.custom_level2_troubleshooting_details,
        "Status": doc.status
        }
    
    # print("body json= ",json.dumps(body))
    # Make the POST request
    webhook_log = frappe.new_doc("Extended Warranty Request Log")
    webhook_log.request_for = "CREATE WARRANTY CLAIM"
    webhook_log.reference_document = doc.name
    webhook_log.headers = str(headers)
    webhook_log.data = str(json.dumps(body))
    webhook_log.user = doc.modified_by
    webhook_log.url = warranty_settings.base_url_claim
    try:
        response = requests.post(warranty_settings.base_url_claim,headers=headers,data=json.dumps(body))
        webhook_log.response = response
        try:
            webhook_log.message = str(response.json())
        except Exception as e:
            print(e)
        
    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))
    webhook_log.insert()