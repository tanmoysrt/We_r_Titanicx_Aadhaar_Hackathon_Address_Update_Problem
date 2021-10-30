from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audit/', include('audit_system.urls')),
    path('', include('aadhaar_update_app.urls'))
]
