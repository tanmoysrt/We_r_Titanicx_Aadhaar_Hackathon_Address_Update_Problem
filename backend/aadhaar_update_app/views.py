from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hackathon_adhaar_solution.helper_functions.jwtutils import encode
from hackathon_adhaar_solution.gateway import user_login_gateway, landlord_login_gateway
from hackathon_adhaar_solution.helper_functions.api_utils import *
from hackathon_adhaar_solution.helper_functions.ekyc_decoder import *
from hackathon_adhaar_solution.helper_functions.communication import send_sms
from hackathon_adhaar_solution.helper_functions.geo_utils import *
from hackathon_adhaar_solution.settings import ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER

from audit_system.audit_function import addAuditLog

from . import models
import hashlib


class ResponseScheme:
    success = False
    payload = {}
    message = ""
    error = ""
    page_show = False

    def set_success(self, success):
        self.success = success

    def set_payload(self, payload):
        self.payload = payload

    def set_message(self, message):
        self.message = message

    def set_error(self, error):
        self.error = error

    def set_page_show(self, page_show):
        self.page_show = page_show

    def to_json(self):
        return {
            "success": self.success,
            "message": self.message,
            "error": self.error,
            "payload": self.payload,
            "page_show": self.page_show
        }

    def to_audit_json(self):
        return {
            "success": self.success,
            "message": self.message,
            "error": self.error,
        }


'''
COMMON ROUTES [NO AUTHORIZATION REQUIRED]

'''

@require_http_methods(["GET"])
def captcha_request(request):
    # print(get_client_ip(request))
    response = ResponseScheme()
    try:
        response_captcha = generate_captcha()
        if response_captcha[0] == "-1" or response_captcha[1] == "-1":
            response.set_success(False)
            response.set_error("Captcha generate failed ! Aadhaar server unreachable")
        else:
            response.set_success(True)
            response.set_payload({
                "captchaTxnId": response_captcha[0],
                "captchaBase64String": response_captcha[1]
            })
            response.set_message("Captcha generated successfully")
    except:
        response.set_success(False)
        response.set_error("Captcha generate failed ! Unexpected Error")

    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
def otp_request(request):
    response = ResponseScheme()

    request_id = str(request.POST.get("request_id", "-1")).strip()
    captcha_txnid = str(request.POST.get("captchaTxnId", "-1")).strip()
    captcha_value = str(request.POST.get("captchaValue", "-1")).strip()
    uid = str(request.POST.get("uid", "-1")).strip()

    transaction_id = uuid.uuid4()
    try:
        if captcha_txnid == "-1" or captcha_value == "-1" or captcha_value == "" or captcha_txnid == "":
            response.set_success(False)
            response.set_error("Captcha txn id or value is missing in request")
        elif uid == "-1" or len(uid) < 12:
            response.set_success(False)
            response.set_error("Invalid uid")
        else:
            response_otp = generate_otp(uid, captcha_txnid, captcha_value, str(transaction_id))
            # print(response_otp)

            if not response_otp[0]:
                response.set_success(False)
                response.set_error(response_otp[1]["message"])
            else:
                response.set_success(True)
                response.set_message(response_otp[1]["message"])
                response.set_payload({
                    "request_transaction_id": str(transaction_id),
                    "otp_transaction_id": response_otp[1]["txnId"]
                })
    except Exception as e:
        print(e)
        response.set_success(False)
        response.set_error("OTP generate failed ! Unexpected Error")

    return JsonResponse(response.to_json(), safe=False)


'''
ALL THE ROUTES REQUIRED BY THE USER WHO IS ASKING CONSENT FOR UPDATE
'''


@require_http_methods(["POST"])
@csrf_exempt
def eKyc_request(request):
    response = ResponseScheme()
    request_transaction_id = str(request.POST.get("request_transaction_id", "-1")).strip()
    uid = str(request.POST.get("uid", "-1")).strip()
    otp_transaction_id = str(request.POST.get("otp_transaction_id", "-1")).strip()
    otp_value = str(request.POST.get("otp", "-1")).strip()

    if request_transaction_id == "-1" or otp_transaction_id == "-1" or otp_value == "-1" or request_transaction_id == "" or otp_transaction_id == "" or otp_value == "" or uid == "" or uid == "-1":
        response.set_success(False)
        response.set_error("All information not filled")
    else:
        fetched_xml = fetch_offline_xml(uid, otp_value, otp_transaction_id, request_transaction_id)
        if not fetched_xml[0]:
            response.set_success(False)
            response.set_error("eKyc Failed please retry")
        else:
            response.set_success(True)
            response.set_message("Successfully eKYC Done")
            eKycXML = fetched_xml[1]
            ekycdoc = OfflinePaperlessKycData(eKycXML)
            request_record = models.RequestRecord.objects.create(
                txn_id=request_transaction_id,
                eKyc_data=json.dumps(ekycdoc.to_json())
            )
            request_record.uid_hash = str(hashlib.sha256(uid.encode()).hexdigest())
            request_record.save()

            response.set_payload({
                "jwt_token": encode(request_transaction_id,0),
                "request_status": request_record.status,
                "request_record_id": str(request_record.id)
            })

            addAuditLog(request, request_record.id, request_record.status, response.to_audit_json(), is_requester=True)

    return JsonResponse(response.to_json(), safe=False)

@require_http_methods(["POST"])
@csrf_exempt
def eKyc_request_with_request_id(request):
    response = ResponseScheme()
    request_id = str(request.POST.get("request_id", "-1")).strip()
    uid = str(request.POST.get("uid", "-1")).strip()
    otp_transaction_id = str(request.POST.get("otp_transaction_id", "-1")).strip()
    otp_value = str(request.POST.get("otp", "-1")).strip()

    if request_id == "-1" or otp_transaction_id == "-1" or otp_value == "-1" or request_id == "" or otp_transaction_id == "" or otp_value == "" or uid == "" or uid == "-1":
        response.set_success(False)
        response.set_error("All information not filled")
    else:
        request_record = models.RequestRecord.objects.get(id=request_id)
        if sha256(uid.encode()).hexdigest() != request_record.uid_hash:
            response.set_success(False)
            response.set_error("UID is not matching")
            response.set_page_show(True)
        else:
            fetched_xml = fetch_offline_xml(uid, otp_value, otp_transaction_id, str(request_record.txn_id))
            if not fetched_xml[0]:
                response.set_success(False)
                response.set_error("eKyc Failed please retry")
            else:
                response.set_success(True)
                response.set_message("Successfully eKYC Done")

                response.set_payload({
                    "jwt_token": encode(request_record.txn_id,0),
                    "request_status": request_record.status,
                    "request_record_id": str(request_record.id)
                })

        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json(), is_requester=True)

    return JsonResponse(response.to_json(), safe=False)

@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def update_number(request):
    response = ResponseScheme()
    mobile_number = str(request.POST.get("mobile_number", "-1")).strip()

    if mobile_number == "-1" or mobile_number == "" or len(mobile_number) < 10:
        response.set_success(False)
        response.set_error("Mobile number not valid")
    else:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        if str(request_record.mobile_no).strip() != "" :
            response.set_success(True)
            response.set_error("Mobile no is updated already")
        else:
            request_record.mobile_no = mobile_number
            request_record.save()
            response.set_success(True)
            response.set_message("Contact no updated")
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())

    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def submit_landlord_number(request):
    response = ResponseScheme()
    landlord_mobile_number = str(request.POST.get("landlord_mobile_number", "-1")).strip()

    if landlord_mobile_number == "-1" or landlord_mobile_number == "" or len(landlord_mobile_number) < 10:
        response.set_success(False)
        response.set_error("Mobile number not valid")
    else:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        if str(request_record.landlord_mobile_no).strip() != "" :
            response.set_success(False)
            response.set_error("Landlord mobile no is updated already and notification has been sent.")
            response.set_page_show(True)
        else:
            request_record.landlord_mobile_no = landlord_mobile_number
            request_record.status = "requested"
            request_record.save()
            send_sms(request_record.mobile_no, "You can check status here. https://main.d3mf157q8c6tmv.amplifyapp.com/r/" + str(request_record.id) + "/")
            send_sms(landlord_mobile_number, "Someone has requested for aaadhar update consent. Click on https://main.d3mf157q8c6tmv.amplifyapp.com/l/" + str(request_record.id) + "/")
            response.set_success(True)
            response.set_message("Request has been submitted & Landlord/neighbour has been notified. You will receive SMS regarding any update")
            response.set_page_show(True)
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())
    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def check_status(request):
    response = ResponseScheme()
    try:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        response.set_success(True)
        response.set_success("Query Successful")
        response.set_payload({
            "status_code": request_record.status,
            "status": request_record.get_status_display()
        })
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())
    except:
        response.set_success(False)
        response.set_error("Record Expired or Not Found")

    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def get_approved_address_of_landlord(request):
    response = ResponseScheme()
    try:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        response.set_success(True)
        response.set_success("Query Successful")
        landlord_eKyc_json = json.loads(request_record.landlord_eKyc_data)
        landlord_address = landlord_eKyc_json["poa"]
        landlord_name = landlord_eKyc_json["poi"]["name"]

        response.set_payload({
            "landlord_name": landlord_name,
            "landlord_address": landlord_address,
            "landlord_mobile_no": request_record.landlord_mobile_no
        })
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())
    except:
        response.set_success(False)
        response.set_error("Record Expired or Not Found")
    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def check_distance_between_address(request):
    response = ResponseScheme()

    json_req_body = json.loads(request.body)
    print(json_req_body)
    if "updated_address" in json_req_body:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        updated_address = POA(json_req_body["updated_address"], from_json=True)
        landlord_eKyc_data = json.loads(request_record.landlord_eKyc_data)
        previous_address = POA(landlord_eKyc_data["poa"], from_json=True)

        # print(updated_address.to_serialized_format())
        # print(previous_address.to_serialized_format())

        updated_address_coordinate = get_coordinate_by_address(updated_address.to_serialized_format())
        previous_address_coordinate = get_coordinate_by_address(previous_address.to_serialized_format())

        distance = get_distance_between_coordinates_meter(updated_address_coordinate[0], updated_address_coordinate[1],
                                                          previous_address_coordinate[0],
                                                          previous_address_coordinate[1])
        if distance >= ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER:
            response.set_success(False)
            response.set_error("Too much difference between landlord address and the updated address. Difference "
                               "need to be less than " + str(
                ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER))
            response.set_payload({
                "distance": distance,
                "allowed_distance": ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER,
                "unit": " meter"
            })
        else:
            response.set_success(True)
            response.set_message("Address is acceptable. You can proceed for aadhaar update submission")
            response.set_payload({
                "distance": distance,
                "allowed_distance": ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER,
                "unit": " meter"
            })
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())
    else:
        response.set_success(False)
        response.set_error("Updated address not sent with request")

    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def submit_address_update(request):
    response = ResponseScheme()

    json_req_body = json.loads(request.body)
    print(json_req_body)

    if "updated_address" in json_req_body and "uid" in json_req_body:
        request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)
        if request_record.status == "updated" :
            response.set_success(False)
            response.set_message("Aadhaar is already updated ! Please refresh")
            response.set_page_show(True)
        else:
            updated_address = POA(json_req_body["updated_address"], from_json=True)
            landlord_eKyc_data = json.loads(request_record.landlord_eKyc_data)
            previous_address = POA(landlord_eKyc_data["poa"], from_json=True)
            previous_user_careof = json.loads(request_record.eKyc_data)["poa"]["careof"]

            updated_address_coordinate = get_coordinate_by_address(updated_address.to_serialized_format())
            previous_address_coordinate = get_coordinate_by_address(previous_address.to_serialized_format())

            distance = get_distance_between_coordinates_meter(updated_address_coordinate[0], updated_address_coordinate[1],
                                                              previous_address_coordinate[0],
                                                              previous_address_coordinate[1])
            if distance >= ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER:
                response.set_success(False)
                response.set_error("Too much difference between landlord address and the updated address. Difference "
                                   "need to be less than " + str(
                    ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER))
                response.set_payload({
                    "distance": distance,
                    "allowed_distance": ALLOWED_DISTANCE_BETWEEN_PREVIOUS_AND_UPDATED_ADDRESS_IN_METER,
                    "unit": " meter"
                })
            else:
                if sha256(str(json_req_body["uid"]).strip().encode()).hexdigest() != request_record.uid_hash:
                    response.set_success(False)
                    response.set_error("You have entered wrong uid ! Please enter the correct one")
                else:
                    updated_address.careof = previous_user_careof

                    models.AddressUpdateLog.objects.create(
                        request_record=request_record,
                        uid=str(json_req_body["uid"]).strip(),
                        previous_address=json.dumps(json.loads(request_record.eKyc_data)["poa"]),
                        updated_address=json.dumps(updated_address.to_json())
                    )

                    request_record.status = "updated"
                    request_record.save()

                    send_sms(request_record.mobile_no, "Your aadhaar address has been updated successfully !")

                    response.set_success(True)
                    response.set_message("Aadhaar Update Completed")
                    response.set_page_show(True)
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())
    else:
        response.set_success(False)
        response.set_error("Updated address not sent with request")

    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@user_login_gateway
def ping_check_request_allowance(request):
    response = ResponseScheme()
    response.set_success(True)
    response.set_message("requests allowed")
    return JsonResponse(response.to_json())


'''
ALL THE LANDLORD ACTION RELATED TASKS ARE DEFINED HERE
'''


@require_http_methods(["POST"])
@csrf_exempt
def landlord_eKyc_request(request):
    response = ResponseScheme()
    request_id = str(request.POST.get("request_id", "-1")).strip()
    uid = str(request.POST.get("uid", "-1")).strip()
    otp_transaction_id = str(request.POST.get("otp_transaction_id", "-1")).strip()
    otp_value = str(request.POST.get("otp", "-1")).strip()

    if request_id == "-1" or otp_transaction_id == "-1" or otp_value == "-1" or request_id == "" or otp_transaction_id == "" or otp_value == "" or uid == "" or uid == "-1":
        response.set_success(False)
        response.set_error("All information not filled")
    else:
        request_record = models.RequestRecord.objects.get(id=request_id)

        if sha256(uid.encode()).hexdigest() == request_record.uid_hash:
            response.set_success(False)
            response.set_error("You can't sign your own address request consent")
            response.set_page_show(True)
        elif request_record.landlord_uid_hash != "":
            response.set_success(False)
            response.set_error("Already a landlord has completed his action. Can't resubmit consent")
            response.set_page_show(True)
        else:
            fetched_xml = fetch_offline_xml(uid, otp_value, otp_transaction_id, request_id)
            if not fetched_xml[0]:
                response.set_success(False)
                response.set_error("eKyc Failed please retry")
            else:
                response.set_success(True)
                response.set_message("Successfully eKYC Done")
                eKycXML = fetched_xml[1]
                ekycdoc = OfflinePaperlessKycData(eKycXML)

                request_record.landlord_eKyc_data = json.dumps(ekycdoc.to_json())
                request_record.landlord_uid_hash = str(hashlib.sha256(uid.encode()).hexdigest())
                request_record.save()

                requested_user_details = json.loads(request_record.eKyc_data)

                response.set_payload({
                    "jwt_token": encode(request_record.txn_id, 1),
                    "request_record_id": str(request_record.id),
                    "user": {
                        "name": requested_user_details["poi"]["name"],
                        "photo": requested_user_details["pht"],
                        "mobile_no": request_record.mobile_no
                    }
                })
        addAuditLog(request, request_record.id, request_record.status, response.to_audit_json(), is_requester=False)
    return JsonResponse(response.to_json(), safe=False)


@require_http_methods(["POST"])
@csrf_exempt
@landlord_login_gateway
def landlord_decision(request):
    response = ResponseScheme()
    approve_action = str(request.POST.get("approve_action", "n")).strip()

    is_approved = True if approve_action == "y" else False
    message = ""
    error = ""
    success = True
    sms_content = ""

    request_record = models.RequestRecord.objects.get(txn_id=request.txn_id)

    if is_approved:
        is_consent_update_possible = True
        # Increase count of consents of landlord
        if models.ConsentCountLog.objects.filter(uid_hash=request_record.landlord_uid_hash).exists():
            consent_log_landlord = models.ConsentCountLog.objects.get(uid_hash=request_record.landlord_uid_hash)
            if consent_log_landlord.consent_count <= consent_log_landlord.consent_limit:
                consent_log_landlord.consent_count = consent_log_landlord.consent_count + 1
                consent_log_landlord.save()
                is_consent_update_possible = True
            else:
                is_consent_update_possible = False
        else:
            models.ConsentCountLog.objects.create(uid_hash=request_record.landlord_uid_hash, consent_count=1)

        if is_consent_update_possible:
            success = True
            message = "Request approved successfully"
            sms_content = "Landlord/neighbour has accepted your request for address update. Kindly confirm address and update your address"
            request_record.status = "approved_by_landlord"
        else:
            success = False
            sms_content = "Landlord/neighbour can't issue you the address due to limit at landlord's side"
            error = "You can't issue further consent due to reach limit of issuing consent"
            request_record.status = "failed_due_to_limit_reach_of_landlord"

    else:
        success = True
        message = "Request rejected successfully"
        sms_content = "Landlord/neighbour has denied your request for address update"
        request_record.status = "rejected_by_landlord"

    send_sms(request_record.mobile_no, sms_content)

    request_record.save()

    response.set_success(success)
    response.set_message(message)
    response.set_error(error)
    response.set_page_show(True)

    addAuditLog(request, request_record.id, request_record.status, response.to_audit_json())

    return JsonResponse(response.to_json(), safe=False)

