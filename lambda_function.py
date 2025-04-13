import json
import os
import requests

HUBSPOT_TOKEN = os.environ['HUBSPOT_ACCESS_TOKEN']
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')

        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Email is required."})
            }

        # Step 1: Search for the contact by email
        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        search_payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email
                        }
                    ]
                }
            ],
            "properties": ["email", "zwitch_newsletter"]
        }

        search_res = requests.post(search_url, headers=HEADERS, json=search_payload)
        if search_res.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Failed to search contact.",
                    "details": search_res.json()
                })
            }

        search_data = search_res.json()
        results = search_data.get("results", [])

        if results:
            # Contact exists
            contact_id = results[0]["id"]
            properties = results[0].get("properties", {})
            current_value = properties.get("zwitch_newsletter")

            if current_value == "true":
                # Already subscribed, return success
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": "Success"})
                }

            # Update the existing contact to set checkbox to true
            update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
            update_payload = {
                "properties": {
                    "zwitch_newsletter": "true"
                }
            }

            update_res = requests.patch(update_url, headers=HEADERS, json=update_payload)
            if update_res.status_code not in [200, 204]:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "message": "Failed to update contact.",
                        "details": update_res.json()
                    })
                }

        else:
            # Contact does not exist, create it with property
            create_url = "https://api.hubapi.com/crm/v3/objects/contacts"
            create_payload = {
                "properties": {
                    "email": email,
                    "zwitch_newsletter": "true"
                }
            }

            create_res = requests.post(create_url, headers=HEADERS, json=create_payload)
            if create_res.status_code not in [200, 201]:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "message": "Failed to create contact.",
                        "details": create_res.json()
                    })
                }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Success"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Server error.",
                "error": str(e)
            })
        }