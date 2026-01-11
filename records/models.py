from django.db import models
from django.utils import timezone
from appointments.models import Appointment

class MedicalFile(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="medical_files",  # <-- ESTE DEBE SER DIFERENTE
    )
    title = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="medical/")
    created_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Expediente #{self.id} (cita #{self.appointment_id})"
