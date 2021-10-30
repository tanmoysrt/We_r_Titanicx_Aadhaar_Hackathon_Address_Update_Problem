import base64
import random
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET

import requests
import json
import uuid

# Constants
appid = "MYAADHAAR"
# Endpoint
captcha_endpoint = "https://stage1.uidai.gov.in/unifiedAppAuthService/api/v2/get/captcha"
otp_endpoint = "https://stage1.uidai.gov.in/unifiedAppAuthService/api/v2/generate/aadhaar/otp"
offline_ekyc_endpoint = "https://stage1.uidai.gov.in/eAadhaarService/api/downloadOfflineEkyc"

EKYC_APP_ID_VALUE = "PORTAL"
EKYC_SHARE_CODE = "1234"


def generate_captcha():
    payload = json.dumps({
        "langCode": "en",
        "captchaLength": "3",
        "captchaType": "2"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", captcha_endpoint, headers=headers, data=payload)
    response_json = response.json()
    #     print(response_json)
    if response_json["status"] != "Success" or response_json["statusCode"] != 200:
        return "-1", "-1"
    # return txnId, base64string Of captcha
    return response_json["captchaTxnId"], response_json["captchaBase64String"]


def generate_otp(uid, captchaTxnId, captchaValue, transactionId):
    payload = json.dumps({
        "uidNumber": str(uid),
        "captchaTxnId": captchaTxnId,
        "captchaValue": captchaValue,
        "transactionId": appid + ":" + transactionId
    })
    headers = {
        'Content-Type': 'application/json',
        'appid': appid,
        'Accept-Language': 'en_in'
    }

    response = requests.request("POST", otp_endpoint, headers=headers, data=payload)
    response_json = response.json()
    if response_json["status"] != "Success":
        return False, response_json
    # print(response_json)
    return True, response_json


def base64_string_to_xml(xml, share_code):
    zf = zipfile.ZipFile(BytesIO(base64.b64decode(xml)))
    zf.setpassword(str(share_code).encode('utf-8'))
    filedata = zf.open(zf.namelist()[0]).read()
    parsedxml = ET.fromstring(filedata, parser=ET.XMLParser(encoding="utf-8"))
    return parsedxml


def fetch_offline_xml(uid, otp, otpTxnId, transactionId):
    share_code = ''.join(random.sample('0123456789', 4))
    payload = json.dumps({
        "aadhaarOrVidNumber": 0,
        "txnNumber": otpTxnId,
        "shareCode": share_code,
        "otp": str(otp),
        "deviceId": None,
        "transactionId": transactionId,
        "unifiedAppRequestTxnId": None,
        "uid": str(uid),
        "vid": None
    })
    headers = {
        'Content-Type': 'application/json',
        'X-Request-ID': str(uuid.uuid4()),
        'appID': EKYC_APP_ID_VALUE,
        'Accept-Language': 'en_in',
        'transactionId': str(transactionId)
    }

    response = requests.request("POST", offline_ekyc_endpoint, headers=headers, data=payload)
    response_json = response.json()
    print(response_json)
    if response_json["status"] != "Success":
        return False, "-1", "-1"
    return True, base64_string_to_xml(response_json["eKycXML"], share_code), response_json["uidNumber"]
