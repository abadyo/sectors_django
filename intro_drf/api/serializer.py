from rest_framework import serializers
from .models import *


class InstituionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institutions
        fields = ["symbol", "date", "top_sellers", "top_buyers"]


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = "__all__"


class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = "__all__"


class IDXSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = IDXSummary
        fields = "__all__"
