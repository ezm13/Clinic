from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "start_time", "end_time", "status", "reason"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        if not start or not end:
            return cleaned

        if end <= start:
            raise ValidationError("La hora de fin debe ser mayor que la hora de inicio.")

        # Validar choques SOLO para el doctor (si lo pasamos)
        if self.doctor:
            overlaps = Appointment.objects.filter(
                doctor=self.doctor,
                start_time__lt=end,
                end_time__gt=start,
            )

            # Si estamos editando una cita, excluirla
            if self.instance and self.instance.pk:
                overlaps = overlaps.exclude(pk=self.instance.pk)

            if overlaps.exists():
                raise ValidationError("Ya existe una cita que se cruza con ese horario.")

        return cleaned
