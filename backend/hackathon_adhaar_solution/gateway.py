from functools import wraps
from django.http import JsonResponse
from hackathon_adhaar_solution.helper_functions.jwtutils import decode
from aadhaar_update_app.models import RequestRecord


def user_login_gateway(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        error = ""
        try:
            token = str(request.headers["Authorization"]).split(" ")[1]
            decoded_token_res = decode(token)
            if not decoded_token_res[0]:
                raise Exception("Token decryption failed")
            request.txn_id = decoded_token_res[1]
            request.is_landlord_neighbour = decoded_token_res[2]
            if decoded_token_res[2] != 0:
                error = "CROSS_USER request. You are not permitted"
            elif not RequestRecord.objects.filter(txn_id=request.txn_id).exists():
                error = "Invalid requests ! Please retry"
            else:
                request_record = RequestRecord.objects.get(txn_id=request.txn_id)
                if request_record.status == "requested":
                    return JsonResponse(
                        {"success": True, "message": "Landlord has not taken any action till now ! Please wait",
                         "error": "", "page_show": True}, status=200)
                elif request_record.status == "rejected_by_landlord":
                    return JsonResponse(
                        {"success": False, "message": "",
                         "error": "Request rejected by landlord", "page_show": True}, status=200)
                elif request_record.status == "rejected_by_system":
                    return JsonResponse(
                        {"success": False, "message": "",
                         "error": "Aadhaar update request rejected by system. For more contact customer care",
                         "page_show": True}, status=200)
                elif request_record.status == "failed_due_to_limit_reach_of_landlord":
                    return JsonResponse(
                        {"success": False, "message": "",
                         "error": "Landlord can't issue you the address due to limit at landlord's side",
                         "page_show": True}, status=200)
                elif request_record.status == "updated":
                    return JsonResponse(
                        {"success": True, "message": "Aadhaar updated successfully",
                         "error": "", "page_show": True}, status=200)

                return view_func(request, *args, **kwargs)
        except KeyError as e:
            error = "Token not found in header"
        except Exception as e:
            error = f"Error : {e}"

        return JsonResponse({"success": False, "message": "", "error": error, "page_show": True}, status=401)
    return wrap


def landlord_login_gateway(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        error = ""
        try:
            token = str(request.headers["Authorization"]).split(" ")[1]
            print(token)
            decoded_token_res = decode(token)
            if not decoded_token_res[0]:
                raise Exception("Token decryption failed")
            request.txn_id = decoded_token_res[1]
            request.is_landlord_neighbour = decoded_token_res[2]
            if decoded_token_res[2] != 1:
                error = "CROSS_USER request. You are not permitted"
            elif not RequestRecord.objects.filter(txn_id=request.txn_id).exists():
                error = "Invalid requests ! Please retry"
            else:
                '''
                CHECK STATUS AND AUTHENTICATE
                '''
                request_record = RequestRecord.objects.get(txn_id=request.txn_id)
                if request_record.status != "requested":
                    return JsonResponse({"success": True, "message": "You have completed your action ! Nothing left behind", "error": ""},
                                        status=200)

                return view_func(request, *args, **kwargs)
        except KeyError as e:
            error = "Token not found in header"
        except Exception as e:
            error = f"Error : {e}"

        return JsonResponse({"success": False, "message": "", "error": error}, status=401)

    return wrap
