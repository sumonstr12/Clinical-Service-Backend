from django.shortcuts import render
from rest_framework.views import APIView
from users.models import *
from appointment.models import *
from users.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .serializers import *


# Create your views here.

class TotalUserCount(APIView):
    # permission_classes = [IsAdmin]
    def get(self, request):
        data = {
            "total_users" : User.objects.count(),
            "total_doctors" : User.objects.filter(role="HEALTHCARE").count(),
            "total_patients" : User.objects.filter(role="PATIENT").count(),
            "total_caregivers" : User.objects.filter(role="CAREGIVER").count(),
            "active_doctors" : HealthCareProvider.objects.filter(is_approved=True).count(),
            "active_caregivers" : CaregiverPatientRelationship.objects.filter(status="active").count(),
            # total appointment section will complete after complete appointment module.
        }

        return Response(
            {
                "status" : True,
                "data" : data
            }, status=status.HTTP_200_OK
        )


class RequestApprovalDoctorView(APIView):
    def get(self, request):
        doctors = HealthCareProvider.objects.filter(is_approved=False).select_related('user')
        serializer = DoctorRequestViewSerializer(doctors, many=True)
        return Response(
            {
                "status" : True,
                "data" : serializer.data
            }, status=status.HTTP_200_OK
        )


class ApproveOrRejectRequestView(APIView):
    def post(self, request):
        is_approved = request.data.get('is_approved')
        health_id = request.data.get('doctor_id')

        print(is_approved, health_id)

        if not is_approved and not health_id:
            return Response(
                {
                    "status" : False,
                    "message" : "is_approved and doctor_id missing."
                }
            )
        if is_approved == "true":
            try:
                doctor = HealthCareProvider.objects.get(id=health_id)

                doctor.is_approved = True
                doctor.save()

            except HealthCareProvider.DoesNotExist:
                return Response(
                    {
                        "status" : False,
                        "message" : "Doctor not available."
                    }
                )

            return Response(
                {
                    "status" : True,
                    "message" : "Doctor approved succesfully."
                }
            )
        else:
            try:
                doctor = HealthCareProvider.objects.get(id=health_id)
                if doctor.is_approved == True:
                    return Response(
                        {
                            "status" : False,
                            "message" : "Doctor already approved."
                        }
                    )
                user = doctor.user
                doctor.delete()
                user.delete()  


            except HealthCareProvider.DoesNotExist:
                return Response(
                    {
                        "status" : False,
                        "message" : "Doctor not available."
                    }
                )

            return Response(
                {
                    "status" : True,
                    "message" : "Doctor Removed succesfully."
                }
            )
