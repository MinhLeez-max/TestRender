"""
URL configuration for projectdatve project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bus_booking.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
