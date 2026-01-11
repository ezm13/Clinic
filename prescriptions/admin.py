from django.contrib import admin
from .models import Prescription, AppointmentFile


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "medication", "created_at")
    list_filter = ("created_at",)
    search_fields = ("medication", "appointment__id")


@admin.register(AppointmentFile)
class AppointmentFileAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "appointment__id")
