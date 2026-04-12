from django.urls import path
from .views import *

urlpatterns = [
    path("admin-login/", AdminLogInView.as_view(), name="admin-login"),
    path('user-count/', TotalUserCount.as_view(), name="user-count"),
    path('doctor-request/', RequestApprovalDoctorView.as_view(), name="doctor-request"),
    path('update-approval-request/', ApproveOrRejectRequestView.as_view(), name="update-approval-request"),
    path('permissions/', PermissionListView.as_view()),
    path('groups/', GroupListCreateView.as_view()),
    path('groups/<int:pk>/', GroupDetailView.as_view()),
    path('users/<int:pk>/assign-groups/', UserGroupAssignView.as_view()),
    path('non-approved-doctors-list/', NonApprovedDoctorListView.as_view(), name="non-approved-doctors-list"),
]

