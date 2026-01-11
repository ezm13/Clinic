from django.contrib import admin
from .models import MedicalFile


@admin.register(MedicalFile)
class MedicalFileAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "appointment__id")
