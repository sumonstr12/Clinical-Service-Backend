from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.permissions import *
from django.db.models import Q

from datetime import datetime



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

        doctor = request.user.healthcareprovider

        # print(request.data)
        serializer = DoctorAvailabilitySerializer( data=request.data,
            context={
                'doctor': doctor
            }
        )

        if serializer.is_valid():

            serializer.save(doctor=doctor)

            return Response(
                {
                    "status": True,
                    "message": "Doctor availability slots created successfully.",
                    "data": serializer.data
                },status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": False,
                "message": "Failed to create doctor availability slots.",
                "errors": serializer.errors
            },status=status.HTTP_400_BAD_REQUEST
        )


class AvailabilitySlotView(APIView):
    permission_classes = [IsPatient | IsCaregiver]
    def post(self, request):
        date_str = request.data.get("day")
        doctor_id = request.data.get("doctor_id")

        try:

            date_object = datetime.strptime(date_str,"%Y-%m-%d")
            python_weekday = date_object.weekday()

            day_mapping = {
                5: 0,  # Saturday
                6: 1,  # Sunday
                0: 2,  # Monday
                1: 3,  # Tuesday
                2: 4,  # Wednesday
                3: 5,  # Thursday
                4: 6   # Friday
            }


            day_of_week = day_mapping[python_weekday]

            slots = DoctorSlot.objects.filter(
                availability__doctor_id=doctor_id,
                availability__day__day_of_week=day_of_week,
                is_booked=False
            )

            serializer = DoctorSlotSerializer(slots, many=True)

            return Response(
                {
                    "status" : True,
                    "data" : serializer.data
                }, status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    "status" : False,
                    "message" : "Failed to load data.",
                    "errors" : str(e)
                }, status=status.HTTP_404_NOT_FOUND
            )
    


class CreateAppointmentView(APIView):

    @transaction.atomic
    def post(self, request):

        user = request.user
        data = request.data.copy()

        data['patient'] = None
        data['caregiver'] = None

        if hasattr(user, 'patient'):

            patient = user.patient
            print(f"Patient ID: {patient}")
            data['patient'] = patient.id

        elif hasattr(user, 'caregiver'):

            caregiver = user.caregiver
            data['caregiver'] = caregiver.id

        else:
            return Response(
                {"error": "Invalid user role"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AppointmentSerializer(data=data)

        if serializer.is_valid():

            slot = serializer.validated_data['slot']
            slot = DoctorSlot.objects.select_for_update().get(id=slot.id)

            if slot.is_booked:
                return Response(
                    {
                        "status": False,
                        "error": "Slot already booked"
                    },status=status.HTTP_400_BAD_REQUEST
                )

            slot.is_booked = True
            slot.save()

            appointment = serializer.save(patient=patient)

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

# class AvailabilitySlotUpdateView(APIView):
#     permission_classes = [IsHealthCareProvider]
#     def put(self, request, pk):
#         user = request.user
#         provider = user.healthcareprovider

#         try:
#             slot = AvailabilitySlot.objects.get(id=pk, provider=provider)

#         except AvailabilitySlot.DoesNotExist:
#             return Response(
#                 {
#                     "status": False,
#                     "message": "Slot not found."
#                 },status=status.HTTP_404_NOT_FOUND
#             )
        
#         serializer = AvailabilitySlotSerializers(
#             instance=slot,
#             data=request.data
#         )

#         if serializer.is_valid():
#             serializer.save(provider=provider)

#             return Response(
#                 {
#                     "status": True,
#                     "message": "Slot Updated Successfully."
#                 },status=status.HTTP_200_OK
#             )
#         return Response(
#             {
#                 "status": False,
#                 "errors": serializer.errors
#             },
#             status=status.HTTP_400_BAD_REQUEST
#         )
    


# class AvailabilitySlotDeleteView(APIView):
#     permission_classes = [IsHealthCareProvider]
#     def delete(self, request, pk):
#         user = request.user
#         provider = user.healthcareprovider
#         if not pk:
#             return Response(
#                 {
#                     "status" : False,
#                     "message" : "pk must be required"
#                 }, status=status.HTTP_404_NOT_FOUND
#             )

#         try:
#             slot = AvailabilitySlot.objects.get(id=pk, provider=provider)
#             slot.delete()
#             return Response(
#                 {
#                     "status" : True,
#                     "message" : "Slots deleted Successfully."
#                 }, status=status.HTTP_200_OK
#             )
        
#         except Exception as e:
#             return Response(
#                 {
#                     "status" : False,
#                     "Errors" : str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST
#             )
        

# class AvailabilitySlotAllView(APIView):
#     def get(self, request):
#         try:
#             slots = AvailabilitySlot.objects.all()
#             serializer = AvailabilitySlotViewSerializers(slots, many=True)

#             return Response(
#                 {
#                     "status" : True,
#                     "data" : serializer.data
#                 }, status=status.HTTP_200_OK
#             )
            
#         except Exception as e:
#             return Response(
#                 {
#                     "status" : False,
#                     "message" : "Failed to load data.",
#                     "errors" : str(e)
#                 }, status=status.HTTP_404_NOT_FOUND
#             )


# class DoctorAvailabilityView(APIView):
#     def get(self, request, doctor_id):
#         try:
#             slots = AvailabilitySlot.objects.filter(provider_id=doctor_id)
#             serializer = AvailabilitySlotViewSerializers(slots, many=True)

#             return Response(
#                 {
#                     "status" : True,
#                     "data" : serializer.data
#                 }, status=status.HTTP_200_OK
#             )
            
#         except Exception as e:
#             return Response(
#                 {
#                     "status" : False,
#                     "message" : "Failed to load data.",
#                     "errors" : str(e)
#                 }, status=status.HTTP_404_NOT_FOUND
#             )