from django.db import models
from django_random_id_model import RandomIDModel

from hackathon_adhaar_solution.settings import MAX_LIMIT_OF_CONSENT_PER_LANDLORD

REQUEST_STATUS = (
    ("request_draft", "Request Drafted"),
    ("requested", "Consent Requested to landlord"),
    ("approved_by_landlord", "Approved by landlord"),
    ("rejected_by_landlord", "Rejected by landlord"),
    ("rejected_by_system", "Rejected by system"),
    ("failed_due_to_limit_reach_of_landlord", "Landlord has reached his limit of issuing consent ! Auto rejection"),
    ("updated", "Aadhaar Details Updated")
)


class RequestRecord(RandomIDModel):
    txn_id = models.TextField(null=True, default="")
    mobile_no = models.CharField(max_length=15, null=True, default="")
    uid_hash = models.TextField(null=True, default="")
    eKyc_data = models.TextField(null=True, default="")
    landlord_mobile_no = models.CharField(max_length=15, null=True, default="")
    landlord_uid_hash = models.TextField(null=True, default="")
    landlord_eKyc_data = models.TextField(null=True, default="")
    status = models.CharField(max_length=50, choices=REQUEST_STATUS, null=True, default="request_draft")
    initiated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class AddressUpdateLog(models.Model):
    request_record = models.OneToOneField(RequestRecord, on_delete=models.CASCADE, related_name="address_update_log")
    uid = models.CharField(max_length=15, null=True, default="")
    previous_address = models.TextField(null=True, default="")
    updated_address = models.TextField(null=True, default="")
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class ConsentCountLog(models.Model):
    uid_hash = models.TextField(null=True, default="", unique=True)
    consent_count = models.IntegerField(null=True, default=0)
    consent_limit = models.IntegerField(null=True, default=MAX_LIMIT_OF_CONSENT_PER_LANDLORD)

