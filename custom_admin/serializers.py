from django.contrib.auth.models import Group, Permission, User
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
    