from django.shortcuts import redirect

def home(request):
    if request.user.is_authenticated:
        # Paciente -> Mis citas
        if hasattr(request.user, "patient_profile"):
            return redirect("/appointments/my/")
        # Doctor/Admin -> Agenda
        return redirect("/appointments/agenda/")
    return redirect("/accounts/login/")

