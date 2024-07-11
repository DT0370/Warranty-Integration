import frappe
from frappe import _
import datetime
from datetime import datetime
import json
import re
import requests, json
from requests.exceptions import HTTPError 

def validate(doc,method=None):
    headers = {
        'X-API-Key': 'asdtfyghjklcghvhbjknlmfxcghbjknlmgcvhbjnkml'
    }
    body = {
        "action": "CREATE WARRANTY CLAIM",
    }
    body ={
        "PolicyNo": doc.custom_policy_no,
        "FirstName": doc.customer_name,
        "LastName":"",
        "CustomerEmail":doc.contact_email,
        "CustomerPhone":doc.contact_mobile,
        "address":doc.address_display,
        "State":doc.custom_state,
        "Landmark":doc.custom_landmark,
        "Model":doc.item_code,
        "SerialNumber":doc.serial_no,
        "PartFailure":doc.complaint,
        "EWEndDate": doc.custom_ew_end_date.isoformat(),
        "Status":"Active"
        }
    
    # print("body json= ",json.dumps(body))
    # Make the POST request
    webhook_log = frappe.new_doc("Extended Warranty Request Log")
    webhook_log.request_for = "CREATE WARRANTY CLAIM"
    webhook_log.reference_document = doc.name
    webhook_log.headers = str(headers)
    webhook_log.data = str(json.dumps(body))
    webhook_log.user = doc.modified_by
    webhook_log.url = 'https://www.warrantyindia.com/360/apiclaim/product/create.php'
    try:
        response = requests.post('https://www.warrantyindia.com/360/apiclaim/product/create.php',headers=headers,data=json.dumps(body))
        webhook_log.response = response
        
    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))
    # print("\n\n\nResponse >>> ",response)
    webhook_log.insert()