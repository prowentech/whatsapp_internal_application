import requests

ACCESS_TOKEN = 'EAAOiBKgZB5skBQuZCZBp6g2J26YNZBor7DVdrqu6ARvkh1nCgDHEzQQKbjo1eCqVg1SLcNtSyN596ZCdZAXWoKMydbCgZAHe6zZBdnce2Jp26gZBmps9T2PchfMxicQSSd7ZBLVnttbj4iBffDw2ZA4TdXmS8TyHwACl4ouMRqXPOZA9Tlyf1w2RJNZBZC2wZBCoDnoMrr75GQOZC1lyZBgDOC0BZBpxTlZBZAnZCc80f8hX4mMB3E8ddGMTgQwvI1le07AUQAopFaAq6ZCBbrLC7pPqm0lqRaboWtqz3ozQZDZD'
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
