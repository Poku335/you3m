from django.contrib import admin
from .models import ConversionTask

@admin.register(ConversionTask)
class ConversionTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'progress', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'youtube_url']
    readonly_fields = ['id', 'created_at', 'updated_at']