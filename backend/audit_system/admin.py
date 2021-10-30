from django.contrib import admin
from audit_system.models import AuditLog

admin.site.register(AuditLog)