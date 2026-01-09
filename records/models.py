from django.conf import settings
from django.db import models
from appointments.models import Appointment

class MedicalFile(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=120, blank=True)  # “Hemograma”, “Rayos X”
    file = models.FileField(upload_to="medical_files/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
