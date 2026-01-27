import json

data = {'object': 'whatsapp_business_account', 'entry': [{'id': '990179309318002', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '919087604440', 'phone_number_id': '562935203577701'}, 'contacts': [{'profile': {'name': 'Sri Vishnu V'}, 'wa_id': '918300048942'}], 'messages': [{'from': '918300048942', 'id': 'wamid.HBgMOTE4MzAwMDQ4OTQyFQIAEhggQUNBOTI5QUVGMEUwNDRBRDY0REIxMEU5RDcyRDE5ODcA', 'timestamp': '1769515054', 'text': {'body': 'Can I know more details'}, 'type': 'text'}]}, 'field': 'messages'}]}]}


print(json.dumps(data))