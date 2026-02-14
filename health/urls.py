from django.urls import path
from .views import *

urlpatterns = [
    path('medical-file-upload', MedicalFileUploadView.as_view(), name="medical-file-upload"),
    
]
