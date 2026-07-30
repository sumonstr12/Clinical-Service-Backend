from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from users.models import *
from appointment.models import *
from users.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from appointment.serializers import *
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken 
from django.db.models import Q


from users.serializers import *


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
    permission_classes = [IsAdmin]

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
        


# Not completed yet
class ApprovedDoctorDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, doctor_id):
        try:
            doctor = HealthCareProvider.objects.select_related("user").get(id=doctor_id, is_approved=True)
            serializer = DoctorRequestViewSerializer(doctor)
            return Response(
                {
                    "status": True,
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except HealthCareProvider.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Doctor not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        

class PatientListView(APIView):
    permission_classes = [IsAdmin | IsHealthCareProvider]

    def get(self, request):

        try:

            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            user = request.user
            if user.role == 'ADMIN':
                patients = Patient.objects.all().order_by("id")
            elif user.role == 'HEALTHCARE':
                doctor = user.healthcareprovider
                print(doctor)
                patients = Patient.objects.filter(
                        patient_appointments__provider=doctor
                    ).distinct()
            else:
                return Response(
                    {
                        "status": False,
                        "message": "User not found."
                    }, status=status.HTTP_404_NOT_FOUND
                )


            
            if search:
                patients = patients.filter(
                    Q(user__full_name__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(user__phone__icontains=search)
                )   

            total_count = patients.count()

            start = (page - 1) * limit
            end = start + limit

            patients = patients[start:end]

            serializer = PatientListSerializer(
                patients,
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

                },status=status.HTTP_200_OK
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

class CaregiverListView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            caregivers = CareGiver.objects.all().order_by("id")

            if search:
                caregivers = caregivers.filter(
                    Q(user__full_name__icontains=search) |
                    Q(user__username__icontains=search)
                )
            
            total_count = caregivers.count()

            start = (page - 1) * limit
            end = start + limit

            caregivers = caregivers[start:end]

            serializer = CaregiverListSerializer(
                caregivers,
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

                },status=status.HTTP_200_OK
            )



        
        except Exception as e:
            return Response(
                {
                    "status" : False,
                    "message" : "Failed to Load Data.",
                    "error" : str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )

class CaregiverDetailView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        try:
            caregiver = CareGiver.objects.get(id=pk)
            serializer = CareGiverPatientRelationViewSerializer(caregiver)

            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except CareGiver.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Caregiver not found."
                }, status=status.HTTP_404_NOT_FOUND
            )

class PatientDetailView(APIView):
    permission_classes = [IsAdmin | IsHealthCareProvider]
    def get(self, request, pk):
        try:
            patient = Patient.objects.get(id=pk)
            serializer = PatientProfileViewSerializer(patient)

            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Patient.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Patient not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class DoctorProfileView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        try:
            doctor = HealthCareProvider.objects.get(id=pk)
            serializer = HealthCareProviderProfileViewSerializer(doctor)
            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )

        except HealthCareProvider.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "HealthCareProvider not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class AppointmentListView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            appointments = Appointment.objects.all().order_by("id")
            if search:
                appointments = appointments.filter(
                    Q(patient__user__full_name__icontains=search) |
                    Q(patient__user__username__icontains=search) |
                    Q(patient__user__email__icontains=search) |
                    Q(provider__user__full_name__icontains=search) |
                    Q(provider__user__username__icontains=search) |
                    Q(issue_description__icontains=search) |
                    Q(status__icontains=search)
                )
            total_count = appointments.count()
            start = (page - 1) * limit
            end = start + limit
            appointments = appointments[start:end]

            serializer = AppointmentSlotViewSerializer(
                appointments,
                many=True
            )

            total_pages = (
                total_count + limit - 1
            ) // limit

            return Response(
            {
                    'status': True,
                    'count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'data': serializer.data
                }, status=status.HTTP_200_OK
            )
        except Appointment.DoesNotExist:
            return Response(
            {
                    'status': False,
                    'message': "Appointment not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class AdminNotificationListView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            queryset = UserNotification.objects.filter(user=user).select_related('notification')

            is_read = request.query_params.get('is_read')
            if is_read is not None:
                if is_read.lower() == "true":
                    queryset = queryset.filter(is_read=True)
                elif is_read.lower() == "false":
                    queryset = queryset.filter(is_read=False)

            from_date = request.query_params.get('from_date')
            to_date = request.query_params.get('to_date')

            if from_date:
                queryset = queryset.filter(created_at__gte=from_date)
            if to_date:
                queryset = queryset.filter(created_at__lt=to_date)

            queryset = queryset.order_by("-created_at")

            # pagination
            page_size = int(request.query_params.get('page_size', 20))
            page =int(request.query_params.get('page', 1))

            start = (page - 1) * page_size
            end = start + page_size
            total_count = queryset.count()

            paginated_queryset = queryset[start:end]

            serializer = UserNotificationListSerializer(paginated_queryset, many=True)
            return Response(
                {
                    'status': True,
                    'data': {
                        'results': serializer.data,
                        'pagination': {
                            'current_page': page,
                            'page_size': page_size,
                            'total_count': total_count,
                            'total_pages': (total_count + page_size -1) // page_size,
                            'has_next': end<total_count,
                            'has_previous': page>0,
                            'next_page': page+1 if end<total_count else None,
                            'previous_page': page-1 if end>0 else None,
                        }
                    }

                }, status=status.HTTP_200_OK
            )

        except Appointment.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Appointment not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class AdminNotificationDetailView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk, *args, **kwargs):
        try:
            notification = get_object_or_404(
                UserNotification,
                pk=pk,
                user=request.user
            )
            serializer = UserNotificationSerializer(notification)
            return Response(
                {
                    'status': True,
                    'data': serializer.data
                }, status=status.HTTP_200_OK
            )
        except UserNotification.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "User notification not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


    def patch(self, request, pk):
        try:
            notification = get_object_or_404(
                UserNotification,
                pk=pk,
                user=request.user
            )

            if 'is_read' in request.data:
                notification.is_read = request.data.get('is_read', notification.is_read)
                notification.save()

                serializer = UserNotificationSerializer(notification)
                return Response(
                    {
                        'status': True,
                        'data': serializer.data
                    }, status=status.HTTP_200_OK
                )
        except UserNotification.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "User notification not found."
                }
            )

    def delete(self, request, pk):
        try:
            notification = get_object_or_404(
                UserNotification,
                pk=pk,
                user=request.user
            )

            notification.delete()

            return Response(
                {
                    'status': True,
                    'message': "User notification deleted."
                }, status=status.HTTP_200_OK
            )
        except UserNotification.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "User notification not found."
                }, status=status.HTTP_404_NOT_FOUND
            )

class MarkNotificationsReadView(APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        try:
            user = request.user
            notification_ids = request.data.get('notification_ids', [])

            if not notification_ids:
                queryset = UserNotification.objects.filter(user=user, is_read=False)
                count = queryset.count()
                queryset.update(is_read=True)

                return Response(
                    {
                        'status': True,
                        'message': f"All {count} notifications marked as read."
                    }, status=status.HTTP_200_OK
                )

            existing_ids = UserNotification.objects.filter(user=user, id__in=notification_ids).values_list('id', flat=True)

            invalid_ids = set(notification_ids) - set(existing_ids)

            if invalid_ids:
                return Response(
                    {
                        'status': False,
                        'message': "Has Invalid ids.",
                        'data': invalid_ids
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            queryset = UserNotification.objects.filter(
                user=user,
                id__in=notification_ids,
                is_read=False
            )
            count = queryset.count()
            queryset.update(is_read=True)

            return Response(
                {
                    'status': True,
                    'message': f"All {count} notifications marked as read."

                }, status=status.HTTP_200_OK
            )

        except UserNotification.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "User notification not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            user = request.user
            unread_count = UserNotification.objects.filter(
                user=user,
                is_read=False
            ).count()

            return Response(
                {
                    'status': True,
                    'data': unread_count
                }, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': 'Failed to get unread count'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )