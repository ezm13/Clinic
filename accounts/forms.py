from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from patients.models import Patient

User = get_user_model()


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label="Recordarme")


class PatientCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    phone = forms.CharField(required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone", ""),
                birth_date=self.cleaned_data.get("birth_date") or None,
                address=self.cleaned_data.get("address", ""),
            )
        return user
