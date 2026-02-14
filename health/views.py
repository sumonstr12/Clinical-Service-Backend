from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
# Create your views here.

                                                                                               
class MedicalFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        serializer = MedicalFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = serializer.validated_data.get("files")
        file_type = serializer.validated_data.get("file_type")

        patient = request.user.patient

        created_id = []

        with transaction.atomic():
            for f in files:
                mf = MedicalFile.objects.create(
                    patient=patient,
                    file=f,
                    file_type=file_type,
                    uploaded_by=request.user
                )
                created_id.append(mf.id)

        return Response(
            {
                "status": True,
                "message": "File Upload Successfully",
                "created_ids": created_id
            },
            status=status.HTTP_201_CREATED
        )
