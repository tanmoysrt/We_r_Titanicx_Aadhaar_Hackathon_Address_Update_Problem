from hackathon_adhaar_solution.settings import FAST2SMS_API_KEY
import requests


def send_sms(mobile_number, message):
    payload = f'''https://www.fast2sms.com/dev/bulkV2?authorization={FAST2SMS_API_KEY}&route=v3&sender_id=TXTIND&message={message}&language=english&flash=0&numbers={mobile_number}'''
    response = requests.get(payload)
    print(response.text)

