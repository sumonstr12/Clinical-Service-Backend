

from django.urls import path
from .views import *

urlpatterns = [
    path('available-doctors/', AvailableDoctorsView.as_view(), name="available-doctors"),
    path('doctor/availability/create/', DoctorAvailabilityCreateView.as_view(), name="doctor/availability/create/"),
    path('doctor/availability/delete/', DoctorAvailabilityDeleteView.as_view(), name="doctor/availability/delete/"),
    path('doctor/doctor-slot-view/', DoctorSlotsView.as_view(), name="doctor/doctor-slot-view"),
    path('doctor/available-slots/', AvailabilitySlotView.as_view(), name="doctor/available-slots/"),
    # path('appointment/slots-view/', AvailabilitySlotView.as_view(), name="appointment/slots-view/"),
    path('appointment/create/', CreateAppointmentView.as_view(), name="appointment/create/"),
    

    # User appointment view
    path('appointment/view/users/', ViewAppointmentsUsersView.as_view(), name="appointment/view/users/"),
#     path('slot-create', AvailabilitySlotCreateView.as_view(), name="slot-create"),
#     path('slot-update/<int:pk>', AvailabilitySlotUpdateView.as_view(), name="slot-update"),
#     path('slot-delete/<int:pk>', AvailabilitySlotDeleteView.as_view(), name="slot-delete"),
#     path('slot-view', AvailabilitySlotAllView.as_view(), name="slot-view"),


    # Doctor Appointment Views url
    path('doctor/appointment/view-list/', AppointmentViewDoctor.as_view(), name="doctor/appointment/view/"),

]