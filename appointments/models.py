from django.conf import settings
from django.db import models
from patients.models import Patient

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pendiente"),
        ("CONFIRMED", "Confirmada"),
        ("CANCELLED", "Cancelada"),
        ("DONE", "Finalizada"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="doctor_appointments")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.patient} - {self.start_time:%Y-%m-%d %H:%M}"
