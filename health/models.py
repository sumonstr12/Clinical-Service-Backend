from django.db import models
from users.models import *
from django.conf import settings
# Create your models here.
User = settings.AUTH_USER_MODEL

class MedicalFile(models.Model):
    File_Type_Choices = (
        ("prescription", "Prescription"),
        ("lab_report", "Lab Report"),
        ("xray", "X-Ray"),
        ("mri", "MRI"),
        ("discharge", "Discharge Summary"),
        ("other", "Other")
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_files")
    file = models.FileField(upload_to="medicalFile/%Y/%m/%d/")
    file_type = models.CharField(max_length=100, choices=File_Type_Choices, default="prescription")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

