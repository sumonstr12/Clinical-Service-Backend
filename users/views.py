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

from django.contrib.auth import get_user_model, authenticate
# Create your views here.

User = get_user_model()


class TempoDataStoredView(APIView):
    def post(self, request, *args, **kwargs):
        # serializer = RegistrationSerializer(data=request.data)

        otp = str(random.randint(111111, 999999))
        print(otp)
        email = request.data.get("email")
        request.data['otp'] = otp
    
        # print(request.data)

        # Set Cache File With Otp
        cache.set("user_data", request.data, timeout=1800)


        # I will build this section later..
        # send_mail(
        #     subject="Your OTP Code........",
        #     message=f"Your OTP code is {otp} .",
        #     from_email="Clinical System<sumon@example.com>",
        #     recipient_list=[email],
        #     fail_silently=False
        # )

        return Response({
                "status": True,
                "message" : "Otp sent successfully..",
                "otp": otp # This is only for test purpose..Not for final Production
            }, status=status.HTTP_200_OK)

class UserRegistrationView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        temp_user = cache.get("user_data")
        cache.delete('user_data')
        # print(temp_user['otp'])
        temp_otp = temp_user.get('otp') if temp_user else None

        # print(temp_otp)

        if temp_user['otp'] == request.data.get("otp"):
            serializer = RegistrationSerializer(data=temp_user)

            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        user = serializer.save()

                    return Response(
                        {   
                            "status" : True,
                            "message": "Registration successful",
                            "user_id": user.id,
                            "username": user.username,
                            "role": user.role
                        },
                        status=status.HTTP_201_CREATED
                    )

                except Exception as e:
                    return Response(
                        {
                            "error": "Registration failed",
                            "details": str(e)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {
                "status" : False,
                "message" : "Invalid OTP."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    


class UserLogInView(APIView):
    permission_classes = []
    def post(self, request, *args):
        username = request.data.get("username")
        password = request.data.get("password")

        # email, phone, username can be used for authenticate but 
        # these should be hundle in frontend
        user = authenticate(username=username, password=password)

        if user:

            role = LoginSerializer(user).data['role']

            is_first_login = LoginSerializer(user).data['is_first_login']


            refresh = RefreshToken.for_user(user)
            response =  Response(
                {
                    "status" : "success",
                    "message" : "Log in successfull.",
                    "role" : role,
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
        serializer = FirstLoginSerializer(
            data = request.data, context={"request" : request}
        )
        print(serializer)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status" : "success",
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
            print(refreshToken)
            if not refreshToken:
                return Response(
                    {
                        "success": False,
                        "message": "Refresh Token required."
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refreshToken)
            print(token)
            token.blacklist()

            return Response(
                {
                    "success" : True,
                    "message" : "Log-Out succesfully."
                },
                status=status.HTTP_200_OK
            )
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
                    "success" : True,
                    "message" : "Profile Update successfull."
                }, status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
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
            else:
                serializer = HealthCareProviderProfileViewSerializer(user.healthcareprovider)


            return Response(
                {
                    "success" : True,
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