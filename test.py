import requests

ACCESS_TOKEN = 'EAAOiBKgZB5skBQnRjAFalCS648bLt6tNc5ksGNy3vAoolKlJ8Kt8yw4LR0qixzyvglCqozX7uq9IVvmPHZC5VpcyiXNVWDLVmggFHNd79ZCU6TOast0jVrlLVfBBJYjt05X4ZBjZBwuh5L7R2tKmLpvyT2wPRkUWiSG9MgkInCY6VKkUE0Y1z0LVRJMMzVuLFWnlB8aPMSdCHdl2Mmyhxe87Nl6gEmeYYZBrSzJyy8AXFaEA9AQPQZB29ZBg3MYnHY8p2h9zDQoLGIEVq2z2sAdXw1YC2gZDZD'
PHONE_NUMBER_ID = '562935203577701'
to_phone = "9659231806"

message = "Test Message from Prowen Technologies"
payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }


url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.post(url, headers=headers, json=payload)
print("response :",res.text)
print(res.status_code)
