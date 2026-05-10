import random
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import *

from django.utils import timezone

from django.contrib.auth import get_user_model, authenticate

from rest_framework_simplejwt.views import TokenRefreshView

# Create your views here.

User = get_user_model()


import random
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TempoDataStoredView(APIView):

    def post(self, request):

        email = request.data.get("email")
        username = request.data.get("username")
        if not email:
            return Response({
                "status": False,
                "message": "Email required !"
            })
        
        if not username:
            return Response({
                "status": False,
                "message": "Username required !"
            })
        
        if User.objects.filter(email=email).exists():  
            return Response({  
                "status": False,
                "message": "Email already exists"
            }, status=status.HTTP_400_BAD_REQUEST)  

 
        if username and User.objects.filter(username=username).exists():  
            return Response({  
                "status": False,
                "message": "Username already exists"
            }, status=status.HTTP_400_BAD_REQUEST)  


        if cache.get(f"otp_limit_{email}"):
            return Response({
                "status": False,
                "message": "Please wait before requesting another OTP"
            })

        otp = str(random.randint(100000, 999999))

        data = request.data.copy()
        data["otp"] = otp

        
        cache.set(f"user_data_{email}", data, timeout=300)

        
        cache.set(f"otp_limit_{email}", True, timeout=60)

        # send email
        # send_mail(...)

        print(otp)

        response =  Response({
            "status": True,
            "message": "OTP sent to your email",
            "otp" : otp
        })

        response.set_cookie(
                key="email",
                value=email,
                secure=False,
                httponly=True,
                max_age= 30 *24*60*60,
                samesite="Lax"
            )
        
        return response



class UserRegistrationView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):

        email = request.COOKIES.get("email")
        # email = request.data.get("email")
        print(f"email: {email}")
        if not email:
            return Response(
                {"status": False, "message": "Session expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_user = cache.get(f"user_data_{email}")
        print(f"Temp_user{temp_user}")
        if not temp_user:
            return Response(
                {"status": False, "message": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_otp = temp_user.get("otp")
        # print(temp_user)
        if str(temp_otp) == str(request.data.get("otp")):
            serializer = RegistrationSerializer(data=temp_user)

            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        user = serializer.save()

                    cache.delete(f"user_data_{email}")
                    print("Done")
                    return Response(
                        {
                            "status": True,
                            "message": "Registration successful",
                            "user_id": user.id,
                            "username": user.username,
                            "role": user.role
                        },
                        status=status.HTTP_201_CREATED
                    )

                except Exception as e:
                    error_message = str(e)  

                    if "email" in error_message.lower(): 
                        message = "Email already exists"  
                    elif "username" in error_message.lower():  
                        message = "Username already exists"  
                    else:
                        message = error_message  
                    return Response(
                        {   
                            "status" : False,
                            "error": "Registration failed",
                            "message": message
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            
            return Response(
                {
                    "status": False,
                    "message": "Invalid OTP(B)."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CaregiverRegistrationView(APIView):
    def post(self, request):
        patient_email = request.data.get("patient_email")

        if not patient_email:
            return Response(
                {
                    "status" : False,
                    "message" : "Patient Email Required!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        patient = User.objects.filter(email=patient_email, role="PATIENT").exists()

        if not patient:
            return Response(
                {
                    "status" : False,
                    "message" : "Patient Not Found!"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CaregiverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()

                    return Response(
                        {
                            "status" : True,
                            "message" : "Caregiver Registration Successfull.Waiting for approval.!"
                        }, status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                error_message = str(e)  

                if "email" in error_message.lower(): 
                    message = "Email already exists"  
                elif "username" in error_message.lower():  
                    message = "Username already exists"  
                else:
                    message = error_message  
                return Response(
                    {  
                        "status" : False,
                        "error": "Registration failed",
                        "message": message
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


# Add extra patient relation with caregiver
class AddNewPatientRelationView(APIView):
    permission_classes=[IsCaregiver]
    def post(self, request):
        patient_email = request.data.get("patient_email")
        
        if not patient_email:
            return Response(
                {
                    "status" : False,
                    "message" : "Email Field is required."
                },status=status.HTTP_400_BAD_REQUEST
            )

        patient = User.objects.filter(email=patient_email, role="PATIENT").exists()
        print(patient)
        if not patient:
            return Response(
                {
                    "status" : False,
                    "message" : "Patient Not Found With this email."
                },status=status.HTTP_400_BAD_REQUEST
            )
        

        serializer = CaregiverPatientRelationshipSerializer(
            data=request.data,
            context={'request': request} 
        )
        
        if serializer.is_valid():
            relation = serializer.save()  
            return Response({
                "status": True,
                "message": "Patient relationship request submitted successfully.",
                "data": {
                    "patient": relation.patient.user.email,
                    "caregiver": relation.caregiver.user.email,
                    "relationship_type": relation.relationship_type,
                    "status": relation.status,
                    "is_primary": relation.is_primary,
                    "can_book_appointment": relation.can_book_appointment,
                    "can_view_medical_records": relation.can_view_medical_records
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CaregiverRequestApprovalView(APIView):
    permission_classes = [IsCaregiver]
    def post(self, request):
        patient_email = request.data.get("patient_email")

        if not patient_email:
            return Response(
                {
                    "status" : False,
                    "message" : "Email Field is required."
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        patient = User.objects.filter(email=patient_email, role="PATIENT").exists()
        # print(patient)
        if not patient:
            return Response(
                {
                    "status" : False,
                    "message" : "Patient Not Found With this email."
                },status=status.HTTP_400_BAD_REQUEST
            )

        print(request.user)
        caregiver = CareGiver.objects.get(user=request.user)
        patient = Patient.objects.get(user__email = patient_email)

        print(f"patient : {patient}")
        try:
            relationship = CaregiverPatientRelationship.objects.get(
                caregiver=caregiver,
                patient=patient
            )
        except CaregiverPatientRelationship.DoesNotExist:
            return Response({
                "status": False,
                "message": "Relationship does not exist"
            })

        if relationship.status == "active":
            return Response(
                {
                    "status" : False,
                    "message": "Patient ALready Approved the request."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        print(relationship.status)
        serializer = CaregiverRequestSerializer(
            data=request.data,
            context={"caregiver": caregiver}  
        )

        if serializer.is_valid():
            verification = serializer.save()

            # send email to patient
            verification_link = f"http://localhost:8000/api/verify-request/{verification.token}/"
            patient_email = verification.relationship.patient.user.email

            print(verification.token)
            print(patient_email)
            # Send email Function -- (Build Later-)

            # from django.core.mail import send_mail
            # send_mail(
            #     subject="Caregiver Approval Request",
            #     message=f"Click to approve caregiver request: {verification_link}",
            #     from_email="noreply@healthcare.com",
            #     recipient_list=[patient_email],
            # )

            return Response(
                {   
                    "status" : True,
                    "message": "Request sent to patient", 
                    "verification_link": verification_link
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status" : False,
                "message" : "Request sent failed.",
                "errors" : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )



# approval view
class ApproveCaregiverRequestView(APIView):

    def get(self, request, token):
        try:
            verification = CaregiverVerification.objects.get(token=token)
        except CaregiverVerification.DoesNotExist:
            return Response(
                {
                    "status" : False,
                    "message" : "Failed to Approved.Try again!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        if verification.is_used:
            return Response(
                {
                    "status" : False,
                    "message" : "Token Already Used."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        if verification.expires_at < timezone.now():
            return Response(
                {
                    "status" : False,
                    "message" : "Token expired.."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        relationship = verification.relationship
        relationship.status = "active"
        relationship.save()

        verification.is_used = True
        verification.save()

        return Response(
            {
                "status" : True,
                "message" : "Request Approved.. "
            }, status=status.HTTP_200_OK
        )

class OtpResendView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {
                    "status" : False,
                    "message" : "Otp sent Failed."
                }
            )
        temp_user = cache.get(f"user_data_{email}")

        if not temp_user:
            return Response(
                {
                    "status" : False,
                    "message" : "Register all the data again."
                }
            )

        otp = str(random.randint(100000, 999999))
        cache.delete(f'user_data_{email}')
        temp_user['otp'] = otp
        print(otp)
        cache.set(f"user_data_{email}", temp_user, timeout=300)

        return Response(
            {
                "status" : True,
                "message" : "Otp sent successfully."
            },status=status.HTTP_200_OK
        )



class UserLogInView(APIView):
    permission_classes = []
    def post(self, request, *args):
        username = request.data.get("username")
        password = request.data.get("password")

        print(username, password)
        # email, phone, username can be used for authenticate but 
        # these should be hundle in frontend
        user = authenticate(username=username, password=password)
        print(f"User: {user}")

        if user:

            role = LoginSerializer(user).data['role']

            is_first_login = LoginSerializer(user).data['is_first_login']
            full_name = LoginSerializer(user).data['full_name']

            if role == "ADMIN":
                return Response(
                    {
                        "status" : False,
                        "message" : "User not found.",
                    }
                , status=status.HTTP_404_NOT_FOUND
                )


            refresh = RefreshToken.for_user(user)
            response =  Response(
                {
                    "status" : True,
                    "message" : "Log in successfull.",
                    "role" : role,
                    "full_name" : full_name,
                    "is_first_login" : is_first_login,
                    "token" : str(refresh.access_token),
                    "refresh_token" : str(refresh)
                }, status=status.HTTP_200_OK
            )

            refresh_token = str(refresh)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                secure=True,
                httponly=True,
                max_age= 30 *24*60*60,
                samesite="strict"
            )
        
            return response



        return Response(
            {
                "status" : False,
                "message" : "Password is incorrect."
            }, status=status.HTTP_400_BAD_REQUEST
        )

class UserFirstLogInView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if not user.is_first_login:
            return Response(
                {
                    "status": False,
                    "message" : "Already Recorded all the Information."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FirstLoginSerializer(
            data = request.data, context={"request" : request}
        )
        # print(serializer)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status" : True,
                    "message": "First Login Profile Setup successfully."
                }, status=status.HTTP_200_OK
            )
        return Response({
            "success" : "false",
            "message" : serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    


class UserLogOutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refreshToken = request.COOKIES.get("refresh_token")
            if not refreshToken:
                return Response(
                    {
                        "success": False,
                        "message": "Refresh Token required."
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refreshToken)
            token.blacklist()

            response = Response(
                {
                    "success" : True,
                    "message" : "Log-Out succesfully."
                },
                status=status.HTTP_200_OK
            )

            response.delete_cookie("refresh_token")

            return response

        except Exception as e:
            return Response(
                {
                    "success" : False,
                    "message" : "An error occured while log out."
                }, status=status.HTTP_400_BAD_REQUEST
            )



class ForgetPasswordView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get("email")
        print(email)
        if not email:
            return Response(
                {
                    "success" : False,
                    "message" : "Email is required."
                }
            )

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()
            print(otp, user)
            # key = email.split("@")[0]
            # user_otp_id = f"otp_id_{key}"
            # # Build email code sendeing option 
            # cache.set(user_otp_id, otp, timeout=600)
            response =  Response(
                {
                    "success" : True,
                    "message" : "Your Otp code sent to your email successfully.",
                    "otp" : otp # Only for test purpose.
                }, status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="email",
                value=email,
                secure=True,
                httponly=True,
                max_age= 5*60,
                samesite="strict"
            )

            return response
        else:
            return Response(
                {
                    "success" : False,
                    "message" : "Email address is not Found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class VerifyOtpView(APIView):
    permission_classes = []
    def post(self, request):
        otp = request.data.get("otp")

        if not otp:
            return Response(
                {
                    "status" : False,
                    "message" : "otp reqired."
                }, status=status.HTTP_404_NOT_FOUND
            )
        
        email = request.COOKIES.get("email")
        print(email)
        if not email:
            return Response(
                {
                    "status" : False,
                    "message" : "Time Out for verification.."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(email=email)

        if otp == user.otp:
            user.otp = "0"
            user.save()

            refresh = RefreshToken.for_user(user)


            response =  Response(
                {
                    "status" : True,
                    "message" : "OTP verification successfull.",
                    "refresh" : str(refresh.access_token)
                }, status=status.HTTP_200_OK
            )

            refresh_token = str(refresh)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                secure=True,
                httponly=True,
                max_age= 30 *24*60*60,
                samesite="strict"
            )

            return response
        
        return Response(
            {
                "status" : False,
                "message" : "OTP verification Failed."
            }
        )
    

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        password = request.data.get("password")

        if not password:
            return Response(
                {
                    "status" : False,
                    "message" : "Password is required."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        if not user:
            return Response(
                {
                    "status" : False,
                    "message" : "User not Found."
                },status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(password)
        user.save()

        return Response(
            {
                "status" : True,
                "message" : "Password Reset Successfull."
            }, status=status.HTTP_200_OK
        )



class UserUpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status" : True,
                    "message" : "Profile Update successfull."
                }, status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "status": False,
                "message": "Profile Update Failed.",
                "errors": serializer.errors
            },status=status.HTTP_400_BAD_REQUEST
        )


class PatientWeightUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = UpdateWeightSerializer(data=request.data)

        if serializer.is_valid():
            print(request.user.patient)
            serializer.save(patient=request.user.patient)
            return Response(
                {
                    "success" : True,
                    "message" : "Update weight history successfull."
                }, status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success" : False,
                "message" : "Update weight history failed.",
                "error" : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        try:
            user = request.user

            print(user.role)
            if user.role == "PATIENT":
                serializer = PatientProfileViewSerializer(user.patient)
            elif user.role == "CAREGIVER":
                serializer = CareGiverProfileViewSerializer(user.caregiver)
            elif user.role == "ADMIN":
                serializer = UserSerializer(user)
            else:
                serializer = HealthCareProviderProfileViewSerializer(user.healthcareprovider)


            return Response(
                {
                    "status" : True,
                    "message" : "Profile Fetched successfull.",
                    "role" : user.role,
                    "data" : serializer.data
                }
            )
        
        except User.DoesNotExist:
            return Response(
                {
                    "status" : False,
                    "message" : "User Profile Not Found."

                }, status=status.HTTP_404_NOT_FOUND
            )
        






class CookieTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get("refresh_token")

        print("Refresh Token from cookie:", refresh_token)

        if not refresh_token:
            return Response(
                {"error": "No refresh token in cookie"},
                status=400
            )

        data = request.data.copy()
        data["refresh"] = refresh_token

        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)