from django.conf import settings
from django.db import models
from appointments.models import Appointment

class ClinicalNote(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    content = models.TextField()
    visible_to_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Nota {self.id} - {self.appointment}"
