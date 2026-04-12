from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.permissions import *
from django.db.models import Q


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



class AvailabilitySlotCreateView(APIView):
    permission_classes = [IsHealthCareProvider]
    # permission_classes = [IsCaregiver]
    def post(self, request):
        user = request.user
        print(user.healthcareprovider)
        provider = user.healthcareprovider
        serializer = AvailabilitySlotSerializers(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(provider=provider)
                return Response(
                    {
                        "status" : True,
                        "message" : "Slots Created successfully."
                    }, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {
                        "status" : False,
                        "message" : "Provider Id required.",
                        "errors" : str(e)
                    }, status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {
                "status" : False,
                "message" : "Slots Create Failed.",
                "errors" : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )
    


class AvailabilitySlotUpdateView(APIView):
    permission_classes = [IsHealthCareProvider]
    def put(self, request, pk):
        user = request.user
        provider = user.healthcareprovider

        try:
            slot = AvailabilitySlot.objects.get(id=pk, provider=provider)

        except AvailabilitySlot.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Slot not found."
                },status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AvailabilitySlotSerializers(
            instance=slot,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(provider=provider)

            return Response(
                {
                    "status": True,
                    "message": "Slot Updated Successfully."
                },status=status.HTTP_200_OK
            )
        return Response(
            {
                "status": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    


class AvailabilitySlotDeleteView(APIView):
    permission_classes = [IsHealthCareProvider]
    def delete(self, request, pk):
        user = request.user
        provider = user.healthcareprovider
        if not pk:
            return Response(
                {
                    "status" : False,
                    "message" : "pk must be required"
                }, status=status.HTTP_404_NOT_FOUND
            )

        try:
            slot = AvailabilitySlot.objects.get(id=pk, provider=provider)
            slot.delete()
            return Response(
                {
                    "status" : True,
                    "message" : "Slots deleted Successfully."
                }, status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {
                    "status" : False,
                    "Errors" : str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )
        

class AvailabilitySlotAllView(APIView):
    def get(self, request):
        try:
            slots = AvailabilitySlot.objects.all()
            serializer = AvailabilitySlotViewSerializers(slots, many=True)

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
