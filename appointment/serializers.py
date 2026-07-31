from .models import *
from rest_framework import serializers
from users.serializers import *
from custom_admin.serializers import *
from users.serializers import *
from datetime import datetime



class AvailableDoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthCareProvider
        fields = ['id', 'user', 'specialization', 'qualification', 'gender', 'date_of_birth', 'img_url', 'cv', 'license_count', 'patient_count']


class DoctorSlotViewSerializer(serializers.ModelSerializer):
    time_slot = serializers.CharField(source='time_slot.start_time', read_only=True)
    class Meta:
        model = DoctorAvailable
        fields = ['id', 'day', 'time_slot']



class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    doctor = AvailableDoctorSerializer(read_only=True)
    time_slot = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = DoctorAvailable
        fields = ['id', 'doctor', 'day', 'time_slot']

    def validate_time_slot(self, value):
        for slot_id in value:
            if not TimeSlot.objects.filter(id=slot_id).exists():
                raise serializers.ValidationError(f"Invalid slot id {slot_id}")
        return value

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    slot_id = serializers.IntegerField(source="time_slot.id")
    start_time = serializers.CharField(source="time_slot.start_time")
    end_time = serializers.CharField(source="time_slot.end_time")

    class Meta:
        model = DoctorAvailable
        fields = ["slot_id", "start_time", "end_time"]


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        slot = data.get('slot')
        appointment_date = data.get('appointment_date')

        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment_date.date(),
                slot.start_time
            )
        )


        if appointment_datetime < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        
        if appointment_date > timezone.now() + timezone.timedelta(days=20):
            raise serializers.ValidationError("Appointment date cannot be more than 20 days in the future.")

        if not slot:
            raise serializers.ValidationError("Slot is required.")


        return data


class AppointmentViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    provider = AvailableDoctorSerializer(read_only=True)
    slot = serializers.CharField(source='slot.start_time', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'provider', 'appointment_date', 'slot', 'issue_description', 'additional_notes', 'created_at', 'status']

class AppointmentSlotViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    provider = AvailableDoctorSerializer(read_only=True)
    patient = PatientProfileViewSerializer(read_only=True)
    caregiver = CareGiverProfileViewSerializer(read_only=True)
    slot = serializers.CharField(source='slot.start_time', read_only=True)
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    appointment_by = serializers.SerializerMethodField(read_only=True)
    appointment_by_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'provider', 'patient', 'caregiver', 'slot', 'patient_name', 'appointment_by', 'appointment_by_role', 'issue_description', 'additional_notes', 'created_at', 'appointment_date', 'status']

    def get_appointment_by(self, obj):
        if obj.patient:
            return obj.patient.user.full_name

        if obj.caregiver:
            return obj.caregiver.user.full_name

        return None

    def get_appointment_by_role(self, obj):
        if obj.caregiver:
            return obj.caregiver.user.role

        if obj.patient:
            return obj.patient.user.role