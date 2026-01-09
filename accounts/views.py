from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render

from .forms import LoginForm, PatientCreateForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        remember = form.cleaned_data.get("remember_me")
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 días
        else:
            self.request.session.set_expiry(0)  # al cerrar navegador

        return response

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("my_appointments")


@login_required
def patient_create(request):
    # ✅ Solo Doctor/Admin: si el user NO es paciente
    if hasattr(request.user, "patient_profile"):
        messages.error(request, "No tienes permiso para crear pacientes.")
        return redirect("my_appointments")

    if request.method == "POST":
        form = PatientCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente creado correctamente.")
            return redirect("my_appointments")
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = PatientCreateForm()

    return render(request, "accounts/patient_form.html", {"form": form})
