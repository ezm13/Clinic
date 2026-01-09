from django.contrib import admin
from .models import Prescription, AppointmentFile

admin.site.register(Prescription)
admin.site.register(AppointmentFile)
