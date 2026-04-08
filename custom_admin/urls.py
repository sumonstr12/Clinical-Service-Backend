from django.urls import path
from .views import *

urlpatterns = [
    path('admin/user-count/', TotalUserCount.as_view(), name="user-count"),
    path('admin/doctor-request/', RequestApprovalDoctorView.as_view(), name="doctor-request"),
    path('admin/update-approval-request/', ApproveOrRejectRequestView.as_view(), name="update-approval-request"),
    
    

]
