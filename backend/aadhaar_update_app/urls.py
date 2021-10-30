from django.urls import path

from . import views

urlpatterns = [
    path("request/captcha/",views.captcha_request),
    path("request/otp/", views.otp_request),
    path("request/ekyc/", views.eKyc_request),
    path("request/ekyc_id/", views.eKyc_request_with_request_id),
    path("update/user_mobile/", views.update_number),
    path("update/landlord_mobile/", views.submit_landlord_number),
    path("status/", views.check_status),
    path("ping/", views.ping_check_request_allowance),
    path("request_approval/ekyc/", views.landlord_eKyc_request),
    path("request_approval/decision/", views.landlord_decision),
    path("request/lanlord_approved_adddress/", views.get_approved_address_of_landlord),
    path("request/verify_address_distance/", views.check_distance_between_address),
    path("request/submit_update/", views.submit_address_update),

]
