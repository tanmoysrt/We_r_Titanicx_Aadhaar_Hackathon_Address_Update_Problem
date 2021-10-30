from django.contrib import admin
from aadhaar_update_app.models import *


admin.site.register(RequestRecord)
admin.site.register(AddressUpdateLog)
admin.site.register(ConsentCountLog)