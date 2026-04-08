from django.db import models
from users.models import *
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL

# Create your models here.
class AvailabilitySlot(models.Model):
    

    provider = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name="AvailabilitySlots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=False)
    max_visit_patient = models.IntegerField(default=0)
    consume_slots = models.IntegerField(default=0)
    appointment_date = models.DateField(default=timezone.now())

    def __str__(self):
        return f"Doctor Name : {self.provider.user.full_name}"
    


class Appointment(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )

    caregiver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caregiver_appointments'
    )

    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='provider_appointments'
    )

    slot = models.ForeignKey(
        'AvailabilitySlot',
        on_delete=models.CASCADE
    )

    issue_description = models.TextField()

    meeting_link = models.URLField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    scheduled = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} -> {self.provider} ({self.scheduled})"