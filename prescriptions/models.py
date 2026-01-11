from django.db import models
from django.utils import timezone
from appointments.models import Appointment


class AppointmentFile(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescription_files",  # <-- CAMBIA ESTO
    )
    title = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="appointments/")
    created_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication} (cita #{self.appointment_id})"


class AppointmentFile(models.Model):
    # ✅ CAMBIO CLAVE: related_name único (ya NO "files")
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescription_files",
    )
    title = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="appointments/")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Archivo #{self.id} (cita #{self.appointment_id})"
