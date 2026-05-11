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


class DoctorSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorSlot
        fields = [ 'id', 'start_time', 'end_time', 'is_booked']
class DoctorAvailabilitySerializer(serializers.ModelSerializer):

    slots = DoctorSlotSerializer(many=True)

    class Meta:
        model = DoctorAvailability
        fields = [
            'day',
            'slots'
        ]

    def validate(self, data):

        doctor = self.context['doctor']
        day = data['day']

        already_exists = DoctorAvailability.objects.filter(
            doctor=doctor,
            day=day
        ).exists()

        if already_exists:
            raise serializers.ValidationError(
                "Availability for this day already exists."
            )

        return data
    

    
    def create(self, validated_data):

        slots_data = validated_data.pop('slots')

        availability = DoctorAvailability.objects.create(
            **validated_data
        )

        for slot_data in slots_data:

            DoctorSlot.objects.create(
                availability=availability,
                **slot_data
            )

        return availability


