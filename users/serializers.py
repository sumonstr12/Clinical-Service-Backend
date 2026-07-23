
from rest_framework import serializers
from .models import *
from django.db import transaction

from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model


User = get_user_model()




# Registration serializers for Patient and HealthCare Provider
class RegistrationSerializer(serializers.Serializer):
     # User
     username = serializers.CharField(max_length=20)
     full_name = serializers.CharField(max_length=100)
     email = serializers.EmailField()
     phone = serializers.CharField(max_length=20)
     password = serializers.CharField(write_only=True)
     role = serializers.ChoiceField(choices=User.Role.choices)
     is_first_login = serializers.BooleanField(required=False)
     is_verified = serializers.BooleanField(required=False)


     # Patient
     cancer_type = serializers.CharField(required=False, allow_blank=True, default="")
     cancer_treatment_type = serializers.CharField(required=False, allow_blank=True, default="")
     medicine_and_dose = serializers.CharField(required=False, allow_blank=True, default="")
     chemo_history_count = serializers.IntegerField(required=False, default=0)
     blood_group = serializers.CharField(required=False, allow_blank=True, default="")
     height = serializers.DecimalField(max_digits=5, decimal_places=2,required=False, default=0)
     gender = serializers.CharField(required=False, allow_blank=True, default="")
     weight = serializers.DecimalField(max_digits=5, decimal_places=2,required=False, default=0)
     date_of_birth = serializers.DateField(required=False, allow_null=True)
     region = serializers.CharField(required=False, allow_blank=True, default="")

     # HealthCareProvider
     specialization = serializers.CharField(required=False)
     qualification = serializers.CharField(required=False)
     img_url = serializers.ImageField(required=False)
     cv = serializers.FileField(required=False)
     license_number = serializers.CharField(required=False)
     license_count = serializers.IntegerField(required=False)


     def validate(self, data):
          role = data.get("role")

          # print(User.Role.PATIENT)
          if role == User.Role.PATIENT:
               required_fields = [
                    
               ]
          # elif role == User.Role.CAREGIVER:
          #           required_fields = [
          #                'relationship'
          #           ]


          elif role == User.Role.ADMIN:
               required_fields = []

          else:
               required_fields = [
                    'specialization',
                    'qualification',
                    'img_url',
                    'cv',
                    'license_number',
                    'license_count',
                    'date_of_birth',
               ]
          

          for field in required_fields:
               if field not in data:
                    raise serializers.ValidationError(
                         {
                              field : "This Field is required for this role."
                         }
                    )
               
          return data
    
     def create(self, validated_data):
          role = validated_data.pop("role")

          # Patient Create
          if role == User.Role.PATIENT:

               # User Create
               user = User.objects.create_user(
                    username = validated_data.pop("username"),
                    full_name = validated_data.pop("full_name"),
                    email = validated_data.pop("email"),
                    password = validated_data.pop("password"),
                    phone = validated_data.pop("phone"),
                    role = role
               )

               medical_fields = [
                    'cancer_type', 'cancer_treatment_type', 'medicine_and_dose',
                    'chemo_history_count', 'blood_group', 'height', 'gender', 'weight',
                    'date_of_birth', 'region'
               ]

               medical_data = {}
               for field in medical_fields:
                    if field in validated_data:
                         value = validated_data.pop(field, None)

                         if value is not None:
                              medical_data[field] = value

               medical = MedicalProfile.objects.create(**medical_data)
               Patient.objects.create(user=user, medical_profile = medical)
               
               
          
          # elif role == User.Role.CAREGIVER:

          #      user = User.objects.create_user(
          #           username = validated_data.pop("username"),
          #           full_name = validated_data.pop("full_name"),
          #           email = validated_data.pop("email"),
          #           password = validated_data.pop("password"),
          #           phone = validated_data.pop("phone"),
          #           role = role
          #      )


          #      CareGiver.objects.create(
          #           user=user,
          #           relationship=validated_data.pop("relationship")
          #      )
          
          elif role == User.Role.ADMIN:
               pass

          else:

               user = User.objects.create_user(
                    username = validated_data.pop("username"),
                    full_name = validated_data.pop("full_name"),
                    email = validated_data.pop("email"),
                    password = validated_data.pop("password"),
                    phone = validated_data.pop("phone"),
                    role = role,
                    is_first_login = validated_data.pop("is_first_login", False)
                    
               )

               HealthCareProvider.objects.create(
                    user=user,
                    specialization=validated_data.pop("specialization"),
                    qualification = validated_data.pop("qualification"),
                    date_of_birth = validated_data.pop("date_of_birth", None),
                    gender = validated_data.pop("gender"),
                    img_url = validated_data.pop("img_url"),
                    cv = validated_data.pop("cv"),
                    license_number = validated_data.pop("license_number"),
                    license_count = validated_data.pop("license_count")
               )
          return user


# Update Serializer for Caregiver Registration


class CaregiverRegistrationSerializer(serializers.Serializer):

     patient_email = serializers.EmailField()
     relationship = serializers.CharField()

     username = serializers.CharField()
     full_name = serializers.CharField()
     email = serializers.EmailField()
     phone = serializers.CharField()
     password = serializers.CharField(write_only=True)

     def create(self, validated_data):

          patient_email = validated_data.pop("patient_email")
          relationship = validated_data.pop("relationship")

          patient = Patient.objects.get(user__email=patient_email)

          user = User.objects.create_user(
               email=validated_data["email"],
               username=validated_data["username"],
               full_name=validated_data["full_name"],
               phone=validated_data["phone"],
               password=validated_data["password"],
               role=User.Role.CAREGIVER
          )

          caregiver = CareGiver.objects.create(
               user=user
          )

          CaregiverPatientRelationship.objects.create(
               patient=patient,
               caregiver=caregiver,
               relationship_type=relationship,
               status="pending"
          )

          return caregiver




# serializer for add new patient with caregiver relation
class CaregiverPatientRelationshipSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = CaregiverPatientRelationship
        fields = [
            "patient_email", 
            "relationship_type",
            "is_primary",
            "can_book_appointment",
            "can_view_medical_records",
            "status",
        ]
        read_only_fields = ["status"] 

    def create(self, validated_data):
        patient_email = validated_data.pop("patient_email")
        patient = Patient.objects.get(user__email=patient_email)
        caregiver = CareGiver.objects.get(user=self.context['request'].user)
        
        
        relation, created = CaregiverPatientRelationship.objects.update_or_create(
            patient=patient,
            caregiver=caregiver,
            defaults=validated_data
        )
        return relation



# serializer for request approval
class CaregiverRequestSerializer(serializers.Serializer):
     patient_email = serializers.EmailField()
     

     def create(self, validated_data):
          patient_email = validated_data["patient_email"]
          
          patient = Patient.objects.get(user__email=patient_email)
          caregiver = self.context["caregiver"]  

          
          relationship = CaregiverPatientRelationship.objects.get(
               patient=patient,
               caregiver=caregiver
          )

          verification = CaregiverVerification.objects.create(
               relationship=relationship
          )

          return verification  
     


# serializer for caregiver list in patient profile
class CaregiverRequestListSerializer(serializers.ModelSerializer):
     caregiver_name = serializers.SerializerMethodField()
     caregiver_email = serializers.SerializerMethodField()
     caregiver_phone = serializers.SerializerMethodField()
     verification_link = serializers.SerializerMethodField()

     class Meta:
          model = CaregiverPatientRelationship
          fields = [
               "id",
               "caregiver_name",
               "caregiver_email",
               "caregiver_phone",
               "relationship_type",
               "status",
               "verification_link"
          ]

     def get_caregiver_name(self, obj):
          return obj.caregiver.user.full_name

     def get_caregiver_email(self, obj):
          return obj.caregiver.user.email

     def get_caregiver_phone(self, obj):
          return obj.caregiver.user.phone

     def get_verification_link(self, obj):
               try:
                    verification = obj.caregiververification
                    print(f"Verification: {verification.id}, Token: {verification.token}")   
                    return (
                         f"http://localhost:8000/api/"
                         f"verify-request/{verification.token}/"
                    )

               except:
                    print(f"No verification found for relationship ID {obj.id}")
                    return None

class LoginSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = [
               "id",
               "username",
               "full_name",
               "email",
               "role",
               "is_first_login",
               "is_verified"
          ]


# This serializer actually for update MedicalProfile model
class FirstLoginSerializer(serializers.Serializer):

     # Medical Profile
     cancer_type = serializers.CharField(allow_blank=True, default="")
     cancer_treatment_type = serializers.CharField( allow_blank=True, default="")
     medicine_and_dose = serializers.CharField( allow_blank=True, default="")
     chemo_history_count = serializers.IntegerField( default=0)
     height = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
     gender = serializers.CharField(allow_blank=True, default="")
     weight = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
     date_of_birth = serializers.DateField( allow_null=True)
     region = serializers.CharField(allow_blank=True, default="")


     def validate(self, data):

          required_fields = [
               'cancer_type',
               'cancer_treatment_type',
               'medicine_and_dose',
               'chemo_history_count',
               'height',
               'gender',
               'weight',
               'date_of_birth',
               'region'
          ]

          for field in required_fields:
               if field not in data:
                    raise serializers.ValidationError(
                         {
                              field : "This Field is required."
                         }
                    )
               
          user = self.context["request"].user
          if not user.is_first_login:
               raise serializers.ValidationError(
                    "First login Setup Already Completed."
               )
          
          if user.role == "HEALTHCARE":
               raise serializers.ValidationError(
                    "Health Care Provider Don't need to setup profile twise."
               )
          return data
     


     def save(self):
          user = self.context["request"].user

          with transaction.atomic():
               patient = Patient.objects.select_related("medical_profile").get(user=user)
               medical = patient.medical_profile

               print(patient)


               medical_fields = [
                    "cancer_type",
                    "cancer_treatment_type",
                    "medicine_and_dose",
                    "chemo_history_count",
                    "height",
                    "weight",
                    "date_of_birth",
                    "gender",
                    "region",
               ]

               for field in medical_fields:
                    if field in self.validated_data:
                         setattr(medical, field, self.validated_data[field])

               medical.save()

               user.is_first_login = "False"
               user.save()

          return user
     



class UserUpdateSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = [
               "username",
               "full_name",
               "email",
               "phone"
          ]
          
          def validate(self, value):
               user = self.instance.id if self.instance else None

               if User.objects.filter(username=value).exclude(id=user).exists():
                    raise serializers.ValidationError("Username already exists.")
               
               
               if User.objects.filter(email=value).exclude(id=user).exists():
                    raise serializers.ValidationError("Email already exists.")
               
               return value
     
          def update(self, instance, validated_data):
               instance.username = validated_data.get("username", instance.username),
               instance.full_name = validated_data.get("full_name", instance.full_name),
               instance.email = validated_data.get("full_name", instance.email),
               instance.phone = validated_data.get("phone", instance.phone)

               instance.save()
               return instance
          


class UpdateWeightSerializer(serializers.ModelSerializer):
     class Meta:
          model = WeightHistory
          fields = [
               "patient",
               "weight",
               "bmi",
               "recorded_at"
          ]
          read_only_fields = ['patient']


# This serializer used only for Patient Profile View.
class MedicalProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = MedicalProfile
          fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = ["username", "full_name", "email", "phone"]

class PatientProfileViewSerializer(serializers.ModelSerializer):
     
     user = UserSerializer(read_only = True)
     weight_history = UpdateWeightSerializer(source='weights', read_only=True, many=True)
     medical_profile = serializers.SerializerMethodField()

     class Meta:
          model = Patient
          fields = '__all__'
          read_only_fields = ['id']

     def get_medical_profile(self, obj):

          try:
               profile = obj.medical_profile

               if profile:
                    return MedicalProfileSerializer(profile).data

          except MedicalProfile.DoesNotExist:
               return None

          return None

class HealthCareProviderProfileViewSerializer(serializers.ModelSerializer):

     user = UserSerializer(read_only=True)
     class Meta:
          model = HealthCareProvider
          fields = '__all__'

class CareGiverProfileViewSerializer(serializers.ModelSerializer):
     user = UserSerializer(read_only=True)
     class Meta:
          model = CareGiver
          fields = '__all__'

