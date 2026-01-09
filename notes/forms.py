from django import forms
from .models import ClinicalNote

class ClinicalNoteForm(forms.ModelForm):
    class Meta:
        model = ClinicalNote
        fields = ["content", "visible_to_patient"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
        }
