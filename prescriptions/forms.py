from django import forms
from .models import Prescription, AppointmentFile


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["medication", "dosage", "frequency", "duration", "notes"]


class AppointmentFileForm(forms.ModelForm):
    class Meta:
        model = AppointmentFile
        fields = ["title", "file"]
