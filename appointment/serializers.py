from .models import *
from rest_framework import serializers
from users.serializers import *


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