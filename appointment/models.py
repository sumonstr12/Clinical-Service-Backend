from django.db import models
from users.models import *
from django.conf import settings
from django.utils import timezone
from users.models import *
from users.models import User

User = settings.AUTH_USER_MODEL


# Create your models here.

class Day(models.Model):
    DAY_CHOICES = [
        (0, 'Saturday'),
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return self.get_day_of_week_display()


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class DoctorAvailable(models.Model):

    doctor = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='availabilities' )
    day = models.ForeignKey( Day, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['doctor', 'day', 'time_slot']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.day } ({self.time_slot})"


class DoctorLeave(models.Model):
    doctor = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='leaves')
    leave_date = models.DateField()
    reason = models.TextField(blank=True)

    class Meta:
        unique_together = ('doctor', 'leave_date')

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.leave_date}"

class Appointment(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_appointments', null=True, blank=True)

    caregiver = models.ForeignKey(CareGiver, on_delete=models.SET_NULL, null=True, blank=True, related_name='caregiver_appointments')

    provider = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='provider_appointments')


    slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, related_name='appointments')

    issue_description = models.TextField()

    additional_notes = models.TextField(blank=True, null=True)

    meeting_link = models.URLField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    appointment_date = models.DateTimeField()


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('provider', 'slot', 'appointment_date')

    def __str__(self):
        return f"{self.patient} -> {self.provider} ({self.appointment_date})"
    
class AppointmentGrant(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='grants')
    accept_date = models.DateField()
    reject_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.appointment.provider.user.full_name} -> {self.reject_reason}"

class Prescription(models.Model):
    pass