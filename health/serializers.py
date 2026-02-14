from rest_framework import serializers
from .models import *


class MedicalFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalFile
        fields = [
            "id",
            "file",
            "file_type",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]



class MedicalFileUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(), allow_empty=False
    )

    file_type = serializers.ChoiceField(
        choices=MedicalFile.File_Type_Choices, required=False, default="prescription"
    )

    