from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from datetime import date


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email,  password=None, **extra_fields):
        if not username:
            return ValueError("Username field must be set!!")
        if not email:
            return ValueError("Email field must be set !!")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extrafields):
        extrafields.setdefault("is_staff", True)
        extrafields.setdefault("is_superuser", True)
        extrafields.setdefault("role", User.Role.ADMIN)

        if extrafields.get("is_staff") is not True:
            return ValueError("Superuser must have is_staff=True")
        if extrafields.get("is_superuser") is not True:
            return ValueError("Superuser must have is_superuser=True")
        return self.create_user(username, email, password, **extrafields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin",
        PATIENT = "PATIENT", "Patient"
        CAREGIVER = "CAREGIVER", "Caregiver"
        HEALTHCARE = "HEALTHCARE", "Healthcare"

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    username = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )
    validation = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} {self.role}"


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects=UserManager()



class MedicalProfile(models.Model):
    cancer_type = models.CharField(max_length=200, blank=True)
    cancer_treatment_type = models.CharField(max_length=400, blank=True)
    medicine_and_dose = models.CharField(max_length=300, blank=True)
    chemo_history_count = models.IntegerField(blank=True, null=True)
    height = models.DecimalField(max_digits=3, decimal_places=2, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    date_of_birth = models.DateField( blank=True, null=True)
    region = models.CharField(max_length=100, blank=True)
    
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year -self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    medical_profile = models.OneToOneField(
        MedicalProfile, on_delete=models.CASCADE
    )
    is_Onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name


    
    
class CareGiver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=20)
    


 
class HealthCareProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    gender = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    img_url = models.ImageField(upload_to="uploads/")
    cv = models.FileField(upload_to="pdf/")
    license_count = models.IntegerField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name
    


class WeightHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='weights')
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    bmi = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateField()

    def save(self, *args, **kwargs):
        # patient_height = self.patient.medical_profile.height
        if self.weight:
            try:
                #
                patient_height = self.patient.medical_profile.height
                print(f"patient height : {patient_height}")
                if patient_height and self.weight:
                    height = float(patient_height) 

                    if height > 0:
                        calc_bmi = float(self.weight) / (height ** 2)
                        self.bmi = round(calc_bmi, 2)
            
            except AttributeError:
                self.bmi = None
                print(f"Error: Patient {self.patient.id} has no MedicalProfile.")

        super(WeightHistory, self).save(*args, **kwargs)

    def __str__(self):
        return self.patient.user.full_name



# Update later 
class RegistrationQueue(models.Model):
    pass