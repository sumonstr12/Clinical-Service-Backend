from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.permissions import *
# Create your views here.

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
