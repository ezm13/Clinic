from django.db import models
from django.utils import timezone


class Prescription(models.Model):
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    medication = models.CharField(max_length=200, null=True, blank=True)
    dosage = models.CharField(max_length=120, blank=True)
    frequency = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication} (cita #{self.appointment_id})"


class AppointmentFile(models.Model):
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="prescription_files",  # ✅ evita choque con records
    )
    title = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="appointments/")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Archivo #{self.id} (cita #{self.appointment_id})"
