import json

from audit_system.models import AuditLog

from hackathon_adhaar_solution.helper_functions.ip_analyzer import get_client_ip, getLocationDetails


def addAuditLog(request, request_id, request_status_current, response,  is_requester=None):
    ip = get_client_ip(request)
    location_data = getLocationDetails(ip)
    location_details = {}
    if location_data[0]:
        location_details = location_data[1]

    audit_record = AuditLog.objects.create(
        request_id=request_id,
        request_status_current=request_status_current,
        ip=ip,
        ip_details=json.dumps(location_details),
        is_error=False if response["success"] else True,
        error=response["error"],
        message=response["message"]
    )

    if is_requester is not None:
        audit_record.is_requester = is_requester
        audit_record.save()
    else:
        try:
            if request.is_landlord_neighbour == 0:
                audit_record.is_requester = True
                audit_record.save()
            elif request.is_landlord_neighbour == 1:
                audit_record.is_requester = False
                audit_record.save()
        except:
            print("Failed")