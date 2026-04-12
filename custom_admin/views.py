from django.shortcuts import render
from rest_framework.views import APIView
from users.models import *
from appointment.models import *
from users.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken 
from django.db.models import Q



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




class AdminLogInView(APIView):
    permission_classes = []
    def post(self, request, *args):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        print(f"User: {user}")

        if user:

            role = LoginSerializer(user).data['role']

            if role != "ADMIN":
                return Response(
                    {
                        "status" : False,
                        "message" : "Wrong Credentials.",
                    }
                , status=status.HTTP_400_BAD_REQUEST
                )

            full_name = LoginSerializer(user).data['full_name']


            refresh = RefreshToken.for_user(user)
            response =  Response(
                {
                    "status" : True,
                    "message" : "Log in successfull.",
                    "role" : role,
                    "full_name" : full_name,
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
    



#  Doctor approved list view already in appoinment views.py file. If you want to see that then check appointment/views.py file.

# Doctor list view those are not approved yet
class NonApprovedDoctorListView(APIView):
    # permission_classes = [IsAdmin]

    def get(self, request):

        try:

            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            doctors = HealthCareProvider.objects.filter(
                is_approved=False
            ).select_related("user").order_by("id")
            
            specialization = request.GET.get("specialization")

            if specialization:
                doctors = doctors.filter(specialization=specialization)
            
            if search:

                doctors = doctors.filter(

                    Q(user__full_name__icontains=search) |
                    Q(specialization__icontains=search) |
                    Q(qualification__icontains=search)

                )

            total_count = doctors.count()

            start = (page - 1) * limit
            end = start + limit

            doctors = doctors[start:end]

            serializer = DoctorRequestViewSerializer(
                doctors,
                many=True
            )

            total_pages = (
                total_count + limit - 1
            ) // limit

            return Response(

                {
                    "status": True,

                    "count": total_count,

                    "total_pages": total_pages,

                    "current_page": page,

                    "data": serializer.data

                },

                status=status.HTTP_200_OK

            )

        except Exception as e:

            return Response(

                {
                    "status": False,
                    "message": "Failed to load data.",
                    "errors": str(e)

                },

                status=status.HTTP_400_BAD_REQUEST

            )