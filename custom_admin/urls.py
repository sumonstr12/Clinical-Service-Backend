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

    path('patient-list/', PatientListView.as_view(), name='patient-list'),
    path('caregiver-list/', CaregiverListView.as_view(), name='caregiver-list'),

    # users details view
    path('caregiver-profile/<int:pk>/', CaregiverDetailView.as_view(), name='caregiver-profile-view'),
    path('patient-profile/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('doctor-profile/<int:pk>/', DoctorProfileView.as_view(), name='doctor-profile-view'),

    # appontent-view stage
    path('appointment-list/', AppointmentListView.as_view(), name='appointment-list'),

    # notification related
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notifications-detail'),

    path('notifications/mark-read/', MarkNotificationsReadView.as_view(), name='mark-notifications-read'),
    path('notifications/unread-count/', UnreadNotificationCountView.as_view(), name='unread-count'),

]