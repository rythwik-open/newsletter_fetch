import json
import os
import requests

HUBSPOT_TOKEN = os.environ['HUBSPOT_ACCESS_TOKEN']
HUBSPOT_LIST_ID = os.environ['HUBSPOT_LIST_ID']
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    try:
        if event['httpMethod'] == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": ""
            }

        body = json.loads(event['body'])
        email = body.get('email')

        if not email:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",  # Allow all origins
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({"message": "Email is required."})
            }

        # Step 1: Create or update contact
        contact_payload = {
            "properties": {
                "email": email
            }
        }

        contact_url = "https://api.hubapi.com/crm/v3/objects/contacts"
        contact_res = requests.post(contact_url, headers=HEADERS, json=contact_payload)

        if contact_res.status_code not in [200, 201]:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "message": "Failed to create contact.",
                    "details": contact_res.json()
                })
            }

        # Step 2: Add to static list
        list_url = f"https://api.hubapi.com/contacts/v1/lists/{HUBSPOT_LIST_ID}/add"
        list_payload = {
            "emails": [email]
        }

        list_res = requests.post(list_url, headers=HEADERS, json=list_payload)

        if list_res.status_code != 200:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "message": "Failed to add to list.",
                    "details": list_res.json()
                })
            }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": "Success"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "message": "Server error.",
                "error": str(e)
            })
        }
