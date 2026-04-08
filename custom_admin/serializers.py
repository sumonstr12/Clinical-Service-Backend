
from rest_framework import serializers
from .models import *
from users.models import *


class DoctorRequestViewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = HealthCareProvider
        fields = ['id', 'full_name', 'specialization', 'qualification', 'gender', 'date_of_birth', 'img_url', 'cv', 'license_count']
        read_only = ['id']

    def get_full_name(self, obj):
        return obj.user.full_name