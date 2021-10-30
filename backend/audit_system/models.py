from django.db import models
from aadhaar_update_app.models import RequestRecord, AddressUpdateLog, REQUEST_STATUS


class AuditLog(models.Model):
    request_id = models.CharField(max_length=50, null=True, editable=False)
    request_status_current = models.CharField(max_length=150, choices=REQUEST_STATUS, null=True)
    ip = models.TextField(default="NOT RECORDED", null=True)
    ip_details = models.TextField(default="{}", null=True)
    is_requester = models.BooleanField(null=True)
    message = models.TextField(null=True)
    error = models.TextField(null=True)
    is_error = models.BooleanField(null=True)
    event_timestamp = models.DateTimeField(auto_now_add=True, null=True)
