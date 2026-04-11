

from django.urls import path
from .views import *

urlpatterns = [
    path('available-doctors/', AvailableDoctorsView.as_view(), name="available-doctors"),
    path('slot-create', AvailabilitySlotCreateView.as_view(), name="slot-create"),
    path('slot-update/<int:pk>', AvailabilitySlotUpdateView.as_view(), name="slot-update"),
    path('slot-delete/<int:pk>', AvailabilitySlotDeleteView.as_view(), name="slot-delete"),
    path('slot-view', AvailabilitySlotAllView.as_view(), name="slot-view"),
]