from django.db import models
from users.models import *
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL

# Create your models here.
class DoctorWorkingDay(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor      = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='working_days')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.get_day_of_week_display()}"


class DoctorSchedule(models.Model):
    doctor        = models.OneToOneField(HealthCareProvider, on_delete=models.CASCADE, related_name='schedule')
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    slot_duration = models.IntegerField(default=30)  # minutes

    def __str__(self):
        return f"{self.doctor.user.full_name} | {self.start_time} - {self.end_time}"  

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

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')

    caregiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='caregiver_appointments')

    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_appointments')


    issue_description = models.TextField()

    meeting_link = models.URLField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    appointment_date = models.DateTimeField()

    appointment_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} -> {self.provider} ({self.appointment_date})"
    

class Prescription(models.Model):
    pass