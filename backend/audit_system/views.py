from django.http import HttpResponse
from django.shortcuts import render
from aadhaar_update_app.models import RequestRecord
from audit_system.models import AuditLog
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u: u.is_superuser, login_url="/admin/login/")
def search(request):
    data = {}
    if request.method == "POST":
        id = request.POST.get("request_id", "")
        if AuditLog.objects.filter(request_id=id).exists():
            data["audit_log_records"] = AuditLog.objects.filter(request_id=id).order_by("-id")
            data["request_record"] = RequestRecord.objects.get(id=id)
            return render(request, "audit_system/show_details.html", data)
        else:
            data["message"] = "Record ID not exists"
    return render(request, "audit_system/id_input.html", data)
