import json

data = {'object': 'whatsapp_business_account', 'entry': [{'id': '990179309318002', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '919087604440', 'phone_number_id': '562935203577701'}, 'statuses': [{'id': 'wamid.HBgMOTE4MzAwMDQ4OTQyFQIAERgSNTM3MkU5RDkyQjIyNjExNzNFAA==', 'status': 'delivered', 'timestamp': '1769511376', 'recipient_id': '918300048942', 'pricing': {'billable': False, 'pricing_model': 'PMP', 'category': 'service', 'type': 'free_customer_service'}}]}, 'field': 'messages'}]}]}


print(json.dumps(data))