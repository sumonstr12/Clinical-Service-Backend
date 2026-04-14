from .models import *
from rest_framework import serializers
from users.serializers import *



class AvailableDoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthCareProvider
        fields = ['id', 'user', 'specialization', 'qualification', 'gender', 'date_of_birth', 'img_url', 'cv', 'license_count', 'patient_count']

class AvailabilitySlotSerializers(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = '__all__'
        read_only_fields = ["provider"]


class AvailabilitySlotViewSerializers(serializers.ModelSerializer):
    provider = HealthCareProviderProfileViewSerializer(read_only=True)

    class Meta:
        model = AvailabilitySlot
        fields = ["provider", "start_time", "end_time", "is_available"]
    

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'