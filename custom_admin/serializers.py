from django.contrib.auth.models import Group, Permission, User
from rest_framework import serializers
from .models import *
from users.models import *

from django.utils import timezone
import datetime


class DoctorRequestViewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = HealthCareProvider
        fields = ['id', 'full_name', 'specialization', 'qualification', 'gender', 'date_of_birth', 'img_url', 'cv', 'license_count']
        read_only = ['id']

    def get_full_name(self, obj):
        return obj.user.full_name
    

class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
    
    def get_full_name(self, obj):
        return obj.user.full_name

    def get_age(self, obj):
        try:
            return obj.medical_profile.age()
        except Exception:
            return None
        

class CaregiverListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    patient_name = serializers.SerializerMethodField()
    relation_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = CareGiver
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.user.full_name

    def get_patient_name(self, obj):
        relation = obj.patient_relations.first()
        return relation.patient.user.full_name if relation else None

    def get_relation_type(self, obj):
        relation = obj.patient_relations.first()
        return relation.relationship_type if relation else None
    
    def get_status(self, obj):
        relation = obj.patient_relations.first()
        return relation.status if relation else None


# Permission based serializer

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source='permissions'
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_ids']

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        instance.permissions.set(permissions)
        return instance

class UserGroupAssignSerializer(serializers.ModelSerializer):
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        source='groups'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'group_ids']

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        instance.groups.set(groups)
        return instance
    

class LoginSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = [
               "id",
               "username",
               "full_name",
               "email",
               "role",
               "is_verified"
          ]

class CaregiverDetailViewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    formatted_created_at = serializers.SerializerMethodField()
    formatted_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            "id",
            'user',
            'notification',
            'is_read',
            'created_at',
            'updated_at',
            'formatted_created_at',
            'formatted_updated_at'

        ]
        read_only_fields = ['user', 'notification', 'created_at', 'updated_at']

    def get_formatted_created_at(self, obj):
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 7:
            return obj.created_at.strftime('%m/%d/%Y')
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago."
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago."
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago."
        else:
            return "Just now."

    def get_formatted_updated_at(self, obj):
            return obj.updated_at.strftime("%b %d, %Y at %I:%M %p ")

class UserNotificationListSerializer(serializers.ModelSerializer):
    notification_title = serializers.CharField(source='notification.title')
    notification_content = serializers.CharField(source='notification.content')
    notification_created_at = serializers.DateTimeField(source='notification.created_at')
    formatted_time = serializers.SerializerMethodField()
    class Meta:
        model = UserNotification
        fields = ['id', 'notification_title', 'notification_content', 'notification_created_at', 'is_read', 'formatted_time']


    def get_formatted_time(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        if diff.days > 7:
            return obj.created_at.strftime('%b %d, %Y')
        elif diff.days > 0:
            return f"day{'s' if diff.days > 1 else ''} ago."
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago."
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago."
        else:
            return "Just now."



