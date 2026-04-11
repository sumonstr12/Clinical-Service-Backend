from django.shortcuts import render
from rest_framework.views import APIView
from users.models import *
from appointment.models import *
from users.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model 



# Create your views here.

User = get_user_model()


class TotalUserCount(APIView):
    permission_classes = [IsAdmin]
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
    permission_classes = [IsAdmin]
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
    permission_classes = [IsAdmin]
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




# Permission Based Code
class PermissionListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        MY_APPS = ['users', 'health', 'appointment'] 

        permissions = Permission.objects.select_related(
            'content_type'
        ).filter(
            content_type__app_label__in=MY_APPS
        )

        serializer = PermissionSerializer(permissions, many=True)
        return Response(
            {
                "status" : True,
                "data" : serializer.data
            }
        )
    


# ─── Group CRUD ────────────────────────────────────────────────────────
class GroupListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        groups = Group.objects.prefetch_related('permissions').all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return Group.objects.prefetch_related('permissions').get(pk=pk)
        except Group.DoesNotExist:
            return None

    def get(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({'error': 'Not found'}, status=404)
        return Response(GroupSerializer(group).data)

    def put(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({'error': 'Not found'}, status=404)
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({'error': 'Not found'}, status=404)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── User → Group Assign ───────────────────────────────────────────────
class UserGroupAssignView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            user = User.objects.prefetch_related('groups').get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        data = {
            'id': user.id,
            'username': user.username,
            'groups': GroupSerializer(user.groups.all(), many=True).data
        }
        return Response(data)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        serializer = UserGroupAssignSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

