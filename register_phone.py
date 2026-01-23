# curl 'https://graph.facebook.com/v24.0/106540352242922/register ' \
# -H 'Content-Type: application/json' \
# -H 'Authorization: Bearer EAAJB...' \
# -d '
# {
#   "messaging_product": "whatsapp",
#   "pin": "212834"
# }

import requests
import json

ACCESS_TOKEN = 'EAAOiBKgZB5skBQjPWaZA7mplPAr5V5dUBNOUwf38mpgz6qMAqS5gF8av7xTXTcL37abgBrZATHZBZCIocV58PCUy0v4ZCo3H4L4EUPuUiWw6ZCpuLPkJcPnTz51cVGh2o279WVczCepKAngJZCw5Rp5oDjioVaN1SC5kxARXVxZA4Y5XhKzUXKRZBKErZBZAVXxVoaVRtP8bvhB517txornJGKwQUJvTEhn1OqqbqxPWmiP8ldn5b6NDR4ZA4w2V1ROSTJNNrSsBcfJIZBYJyPttqpsY2lJshE7wZDZD'
PHONE_NUMBER_ID = '562935203577701'
VERIFY_TOKEN = 'prowen_secret_key'
to_phone = '8300048942'
message = 'Hi This is a Test Message from Prowen Technologies!'
TEMPLATE_NAMES = ['hotel_analytics_video']
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

try:
    response = requests.post(url, headers=headers, json=payload)
    print(response)
    print(response.text)
    response.raise_for_status()
except Exception as e:
    print(e)
    print(e.__traceback__.tb_lineno)
#
# ACCESS_TOKEN = 'EAAOiBKgZB5skBQuCSSCGfAaq4BlEsrJSfrMOUGqrpI5SPZC9GOltrv4dNUsb6ykwZC3Jfxmh2fE1TPA7tCwop7GcoSpvHUmHjW6TlymqdNUEg4BY2v4knjoW4B3k2MiZAB7GCOMZBWZA0qKws0nvZAME3YQNAABtusH1q9ZC0OtnfFkFJiVzgd4yNzZB60V7JlaQ3zCdZBrAAXWWDcJ6SA6ZCtRm8LiXfzpoweOQRe0mEsQwrZCopZAvauTGaBt7EddHcTvp5bsCmFhLRXhaBjAAvn1mavfp7qqIZD'
#
# headers = {
#             "Authorization": f"Bearer {ACCESS_TOKEN}",
#             "Content-Type": "application/json"
#         }
#
#
# payload = {
#   "messaging_product": "whatsapp",
#   "pin": "908760"
# }
#
# url = 'https://graph.facebook.com/v24.0/562935203577701/register'
#
# response = requests.post(url,headers=headers,json=payload)
# print(response)
# print(response.text)




