from rest_framework import serializers
from .models import ConversionTask

class ConversionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionTask
        fields = ['id', 'youtube_url', 'title', 'status', 'progress', 'error_message', 'created_at']
        read_only_fields = ['id', 'title', 'status', 'progress', 'error_message', 'created_at']

class ConversionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionTask
        fields = ['id', 'status', 'progress', 'title', 'error_message']