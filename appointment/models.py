from django.db import models
from users.models import *
from django.conf import settings
from django.utils import timezone


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



class DoctorAvailability(models.Model):

    doctor = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='availabilities' )

    day = models.ForeignKey( Day, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['doctor', 'day']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.day}"
    

class DoctorSlot(models.Model):

    availability = models.ForeignKey( DoctorAvailability, on_delete=models.CASCADE, related_name='slots')

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
class DoctorWorkingDay(models.Model):
    doctor      = models.ForeignKey(HealthCareProvider, on_delete=models.CASCADE, related_name='working_days')
    days = models.ManyToManyField(Day, related_name='doctors')


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