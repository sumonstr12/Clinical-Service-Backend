from .models import *
from rest_framework import serializers
from users.serializers import *



class AvailableDoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthCareProvider
        fields = ['id', 'user', 'specialization', 'qualification', 'gender', 'date_of_birth', 'img_url', 'cv', 'license_count', 'patient_count']


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        slot = data.get('slot')
        appointment_date = data.get('appointment_date')

        if appointment_date < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")

        if not slot:
            raise serializers.ValidationError("Slot is required.")

        if slot.is_booked:
            raise serializers.ValidationError("This slot is already booked.")

        return data