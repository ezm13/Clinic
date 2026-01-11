from django.db import models
from django.utils import timezone


class MedicalFile(models.Model):
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="medical_files",  # ✅ distinto a prescription_files
    )
    title = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="medical_records/")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"MedicalFile #{self.id} (cita #{self.appointment_id})"
