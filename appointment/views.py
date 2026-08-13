from logging import exception

from django.shortcuts import render

from users.models import *
from .models import *
from .serializers import *
from custom_admin.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.permissions import *
from django.db.models import Q

from datetime import datetime
from django.utils import timezone



# Create your views here.


class AvailableDoctorsView(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request):

        try:

            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            doctors = HealthCareProvider.objects.filter(
                is_approved=True
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

            serializer = AvailableDoctorSerializer(
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

class DoctorAvailabilityCreateView(APIView):

    permission_classes = [IsHealthCareProvider]

    def post(self, request):

        user = request.user
        provider = user.healthcareprovider

        time_slots = request.data.get("time_slot", [])

        serializer = DoctorAvailabilitySerializer(data=request.data)

        if serializer.is_valid():
            test = serializer.validated_data
            print(f"Validated data: {test}")
            day_id = serializer.validated_data['day'].id
            print(f"day_id: {day_id}")
            created = 0
            skipped = 0

            for slot_id in time_slots:

                exists = DoctorAvailable.objects.filter(
                    doctor=provider,
                    day_id=day_id,
                    time_slot_id=slot_id
                ).exists()

                if exists:
                    skipped += 1
                    continue

                DoctorAvailable.objects.create(
                    doctor=provider,
                    day_id=day_id,
                    time_slot_id=slot_id
                )

                created += 1

            return Response({
                "status": True,
                "message": "Availability processed successfully.",
                "created": created,
                "skipped": skipped
            }, status=201)

        return Response({
            "status": False,
            "message": "Failed to create availability.",
            "errors": serializer.errors
        }, status=400)
    

class DoctorSlotsView(APIView):

    permission_classes = [IsHealthCareProvider]
    def get(self, request):

        day = request.GET.get("day")
        doctor_id = request.user.healthcareprovider.id
        print(f"Received day: {day}, doctor_id: {doctor_id}")

        try:
            slots = DoctorAvailable.objects.filter(doctor_id=doctor_id, day_id=day).select_related('time_slot')
            serializer = DoctorSlotViewSerializer(slots, many=True)

            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Failed to load data.",
                    "errors": str(e)
                }, status=status.HTTP_404_NOT_FOUND
            )

class DoctorAvailabilityDeleteView(APIView):

    permission_classes = [IsHealthCareProvider]

    def delete(self, request):

        user = request.user
        provider = user.healthcareprovider

        day_id = request.data.get("day")
        time_slot_id = request.data.get("time_slot")

        if not day_id or not time_slot_id:
            return Response({
                "status": False,
                "message": "day and time_slot are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = DoctorAvailable.objects.filter(doctor=provider, day_id=day_id, time_slot_id=time_slot_id).delete()

        if deleted:
            return Response({
                "status": True,
                "message": "Availability deleted successfully."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": False,
                "message": "No matching availability found to delete."
            }, status=status.HTTP_404_NOT_FOUND)
class AvailabilitySlotView(APIView):
    
    def post(self, request):

        doctor_id = request.data.get("doctor")
        date = request.data.get("date")

        print(f"Received doctor_id: {doctor_id}, date: {date}")

        if not doctor_id or not date:
            return Response(
                {
                    "status": False,
                    "message": "doctor_id and date are required."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        try:

            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            day = ((date_obj.weekday() + 2) % 7) + 1

            available_slots = DoctorAvailable.objects.filter(
                doctor_id=doctor_id,
                day=day
            ).select_related('time_slot')

            appointments_on_date = Appointment.objects.filter(
                provider_id=doctor_id,
                appointment_date=date_obj
            ).select_related('slot')

            booked_slot_ids = appointments_on_date.values_list(
                'slot_id',
                flat=True
            )

            free_slots = available_slots.exclude(
                time_slot_id__in=booked_slot_ids
            )


            serializer = AvailabilitySlotSerializer(free_slots, many=True)

            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Failed to load data.",
                    "errors": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )

class CreateAppointmentView(APIView):

    @transaction.atomic
    def post(self, request):

        user = request.user
        data = request.data.copy()

        doctor_id = request.data.get("provider")
        appointment_date = request.data.get("appointment_date")
        slot_id = request.data.get("slot")

        date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
        date = date_obj.strftime("%b %d")

        app_time = TimeSlot.objects.get(id=slot_id).start_time
        formatted_time = app_time.strftime("%I:%M %p")


        try:

            doctor = HealthCareProvider.objects.get(id=doctor_id)


        except HealthCareProvider.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "TimeSlot or Doctor does not exist.",
                }
            )



        if user.role == 'CAREGIVER':
            patient_id = request.data.get("patient_id")
            patient = Patient.objects.get(id=patient_id)

            is_related = CaregiverPatientRelationship.objects.filter(
                caregiver=user.caregiver,
                patient=patient,
                status="active"
            ).exists()


            if not is_related:
                return Response(
                    {
                    "status": False,
                    "message": "Patient id not match.",
                    }, status=status.HTTP_400_BAD_REQUEST
                )


        data['patient'] = None
        data['caregiver'] = None

        patient = None
        caregiver = None

        if hasattr(user, 'patient'):

            patient = user.patient
            data['patient'] = patient.id

        elif hasattr(user, 'caregiver'):
            if is_related:
                patient = Patient.objects.get(id=patient_id)

            data['patient'] = patient.id
            caregiver = user.caregiver
            data['caregiver'] = caregiver.id

        else:
            return Response(
                {"error": "Invalid user role"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AppointmentSerializer(data=data)

        if serializer.is_valid():
            if patient:
                appointment = serializer.save(patient=patient)

                user = patient.user
                create_notification(
                    "Appointment Confirmed!",
                    f"Your appointment with {doctor.user.full_name} is set for {date} at {formatted_time}.",
                    user
                )


            else:
                appointment = serializer.save(patient=patient, caregiver=caregiver)

                users = []
                users.append(patient.user)
                users.append(caregiver.user)

                create_notification(
                    "Appointment Confirmed!",
                    f"Your appointment with {doctor.user.full_name} is set for {date} at {formatted_time}.",
                    users
                )



            return Response(
                {
                    "status": True,
                    "message": "Appointment created successfully",
                    "appointment_id": appointment.id
                }, status=status.HTTP_201_CREATED)

        return Response(
            {
                "status": False,
                "message": "Failed to create appointment",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )

class RelatedPatientCaregiverView(APIView):
    permission_classes = [IsCaregiver]
    def get(self, request):
        caregiver = request.user.caregiver
        try:

            patients = Patient.objects.filter(
                caregiver_relations__caregiver=caregiver
            ).distinct()

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Failed to load data.",
                }
            )

        serializer = PatientListSerializer(
            patients,
            many=True
        )
        return Response(
            {
                "status": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )


class ViewAppointmentsUsersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if hasattr(user, 'patient'):
            appointments = Appointment.objects.filter(patient=user.patient).select_related('provider', 'slot')

        elif hasattr(user, 'caregiver'):
            appointments = Appointment.objects.filter(caregiver=user.caregiver).select_related('provider', 'slot')

        elif hasattr(user, 'healthcareprovider'):
            appointments = Appointment.objects.filter(provider=user.healthcareprovider).select_related('patient', 'slot')

        else:
            return Response(
                {"error": "Invalid user role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AppointmentViewSerializer(appointments, many=True)

        return Response(
            {
                "status": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )

class AppointmentViewDoctor(APIView):
    permission_classes = [IsHealthCareProvider]
    def get(self, request):
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))

            provider = request.user.healthcareprovider
            appointments = Appointment.objects.filter(provider=provider).select_related('patient', 'slot')
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

            total_pages = ( total_count + limit - 1 ) // limit

            return Response(
                {
                    'status': True,
                    'count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'data': serializer.data
                }, status=status.HTTP_200_OK
            )
        except exception as e:
            return Response(
            {
                    'status': False,
                    'message': "Appointment not found.",
                    'errors' : str(e)
                }, status=status.HTTP_404_NOT_FOUND
            )


class StatusUpdateByDoctor(APIView):
    permission_classes = [IsHealthCareProvider]
    def post(self, request):
        try:
            appointment_id = request.data.get('appointment_id')
            new_status = request.data.get('status')
            doctor = request.user.healthcareprovider
            if not appointment_id:
                return Response(
                    {
                        'status': False,
                        'message': "Appointment ID not found.",
                    }, status=status.HTTP_404_NOT_FOUND
                )
            print(appointment_id)
            print(new_status)
            print(doctor)

            appointment = Appointment.objects.get(id=appointment_id, provider=doctor)

            valid_statuses = []
            for choice in Appointment.STATUS_CHOICES:
                valid_statuses.append(choice[0])

            if new_status not in valid_statuses:
                print('not a valid status')
                return Response(
                    {
                        'status': False,
                        'message': "Invalid status.",

                    }, status=status.HTTP_400_BAD_REQUEST
                )

            appointment.status = new_status
            appointment.save()
            return Response(
                {
                    'status': True,
                    'message': "Appointment updated successfully.",
                }, status=status.HTTP_200_OK
            )

        except Appointment.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Appointment not found.",
                }, status=status.HTTP_404_NOT_FOUND
            )