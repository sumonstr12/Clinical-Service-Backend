
from django.contrib import admin
from django.urls import path, include

api_urlpaterns = [
    path("", include("users.urls")),
    path("", include("health.urls")),
    path("", include("appointment.urls")),
    path("", include("custom_admin.urls")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(api_urlpaterns)),
]
