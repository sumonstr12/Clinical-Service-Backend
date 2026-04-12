
from django.urls import path
from .views import *
# from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path('user-registration', TempoDataStoredView.as_view(), name='user-registration'),
    path('caregiver-registration', CaregiverRegistrationView.as_view(), name='caregiver-registration'),
    path('user-login', UserLogInView.as_view(), name='user-login'),
    path('verify-otp-registration', UserRegistrationView.as_view(), name='verify-otp-registration'),
    path('user-login/update-profile', UserFirstLogInView.as_view(), name='user-login/update-profile'),
    path('user-logout', UserLogOutView.as_view(), name="user-logout"),
    path('forget-password', ForgetPasswordView.as_view(), name="forget-password"),
    path('verify-otp',VerifyOtpView.as_view(), name='verify-otp'),
    path('reset-password', UpdatePasswordView.as_view(), name='reset-password'),
    path('update-profile', UserUpdateProfileView.as_view(), name='update-profile'),
    path('update-weight', PatientWeightUpdateView.as_view(), name="update-weight"),
    path('user-profile', UserProfileView.as_view(), name='user-profile'),


    path('sent-approve-request', CaregiverRequestApprovalView.as_view(), name='arrove-request'),
    path('add-new-patient', AddNewPatientRelationView.as_view(), name='add-new-patient'),
    path('verify-request/<uuid:token>/', ApproveCaregiverRequestView.as_view(), name='verify-request'),
    path('otp-resend', OtpResendView.as_view(), name='otp-resend'),


    path('token/refresh/', CookieTokenRefreshView.as_view()),
]


