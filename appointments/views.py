from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from notes.forms import ClinicalNoteForm
from notes.models import ClinicalNote

from prescriptions.forms import AppointmentFileForm, PrescriptionForm
from prescriptions.models import AppointmentFile, Prescription

from .forms import AppointmentForm
from .models import Appointment
from .pdf import build_prescriptions_pdf
from .utils import log_action
from django.db.models import Count, Q
from django.core.paginator import Paginator



# ---------------------------
# Helpers
# ---------------------------

def _safe_log_action(request, **kwargs):
    try:
        return log_action(request, **kwargs)
    except TypeError:
        minimal_keys = ("appointment", "action", "message")
        minimal = {k: v for k, v in kwargs.items() if k in minimal_keys}
        try:
            return log_action(request, **minimal)
        except Exception:
            return None


def _is_patient(user) -> bool:
    return hasattr(user, "patient_profile")


def _patient_can_touch(appt: Appointment, user) -> bool:
    return _is_patient(user) and appt.patient.user_id == user.id


# ---------------------------
# LISTAS / AGENDA
# ---------------------------

@login_required
def my_appointments(request):
    is_patient = _is_patient(request.user)

    if is_patient:
        qs = Appointment.objects.filter(
            patient=request.user.patient_profile
        ).order_by("-start_time")
    else:
        qs = Appointment.objects.all().order_by("-start_time")

    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": qs, "is_patient": is_patient},
    )


@login_required
def doctor_agenda(request):
    # Si es paciente, no puede ver agenda general
    if _is_patient(request.user):
        return redirect("my_appointments")

    date_str = request.GET.get("date")
    selected_date = parse_date(date_str) if date_str else timezone.localdate()

    start_day = timezone.make_aware(
        timezone.datetime.combine(selected_date, timezone.datetime.min.time())
    )
    end_day = timezone.make_aware(
        timezone.datetime.combine(selected_date, timezone.datetime.max.time())
    )

    appointments = Appointment.objects.filter(
        doctor=request.user,
        start_time__range=(start_day, end_day),
    ).order_by("start_time")

    return render(
        request,
        "appointments/doctor_agenda.html",
        {"appointments": appointments, "today": selected_date},
    )

from django.db.models import Count, Q  # <-- agrega esto arriba si no lo tienes

@login_required
def doctor_dashboard(request):
    # Si es paciente, no puede ver dashboard
    if hasattr(request.user, "patient_profile"):
        return redirect("my_appointments")

    today = timezone.localdate()
    now = timezone.now()

    start_day = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    end_day = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.max.time())
    )

    # Solo citas del doctor logueado
    base_qs = Appointment.objects.filter(doctor=request.user)

    # Citas de HOY
    today_qs = base_qs.filter(start_time__range=(start_day, end_day))

    today_counts = today_qs.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="PENDING")),
        confirmed=Count("id", filter=Q(status="CONFIRMED")),
        cancelled=Count("id", filter=Q(status="CANCELLED")),
        done=Count("id", filter=Q(status="DONE")),
    )

    # Próximas citas (desde ahora)
    upcoming_qs = base_qs.filter(start_time__gte=now).order_by("start_time")
    upcoming_counts = upcoming_qs.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="PENDING")),
        confirmed=Count("id", filter=Q(status="CONFIRMED")),
        cancelled=Count("id", filter=Q(status="CANCELLED")),
        done=Count("id", filter=Q(status="DONE")),
    )

    next_appointments = upcoming_qs[:10]

    return render(
        request,
        "appointments/doctor_dashboard.html",
        {
            "today": today,
            "today_counts": today_counts,
            "upcoming_counts": upcoming_counts,
            "next_appointments": next_appointments,
        },
    )



# ---------------------------
# DETALLE (Notas / Recetas / Archivos)
# ---------------------------

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    is_patient = _is_patient(request.user)

    # Si es paciente, solo puede ver SU cita
    if is_patient and appointment.patient.user_id != request.user.id:
        messages.error(request, "No tienes permiso para ver esta cita.")
        return redirect("my_appointments")

    notes_qs = appointment.notes.all()
    prescriptions = appointment.prescriptions.all()
    files = appointment.files.all()

    form = None
    prescription_form = None
    file_form = None

    if not is_patient:
        # doctor dueño
        if appointment.doctor_id != request.user.id:
            messages.error(request, "No tienes permiso para ver esta cita.")
            return redirect("doctor_agenda")

        form = ClinicalNoteForm()
        prescription_form = PrescriptionForm()
        file_form = AppointmentFileForm()

        if request.method == "POST":
            if "save_note" in request.POST:
                form = ClinicalNoteForm(request.POST)
                if form.is_valid():
                    n = form.save(commit=False)
                    n.appointment = appointment
                    n.author = request.user
                    n.save()

                    _safe_log_action(
                        request,
                        appointment=appointment,
                        action="CREATE",
                        object_type="ClinicalNote",
                        object_id=n.id,
                        message="Creó una nota clínica",
                    )

                    messages.success(request, "Nota guardada.")
                    return redirect("appointment_detail", pk=appointment.id)

            elif "save_prescription" in request.POST:
                prescription_form = PrescriptionForm(request.POST)
                if prescription_form.is_valid():
                    p = prescription_form.save(commit=False)
                    p.appointment = appointment
                    p.save()

                    _safe_log_action(
                        request,
                        appointment=appointment,
                        action="CREATE",
                        object_type="Prescription",
                        object_id=p.id,
                        message="Creó una receta (medicamento)",
                    )

                    messages.success(request, "Receta guardada.")
                    return redirect("appointment_detail", pk=appointment.id)

            elif "save_file" in request.POST:
                file_form = AppointmentFileForm(request.POST, request.FILES)
                if file_form.is_valid():
                    f = file_form.save(commit=False)
                    f.appointment = appointment
                    f.save()

                    _safe_log_action(
                        request,
                        appointment=appointment,
                        action="CREATE",
                        object_type="AppointmentFile",
                        object_id=f.id,
                        message="Subió un archivo (Rayos X)",
                    )

                    messages.success(request, "Archivo subido.")
                    return redirect("appointment_detail", pk=appointment.id)

    if is_patient:
        notes_qs = notes_qs.filter(visible_to_patient=True)

    return render(
        request,
        "appointments/appointment_detail.html",
        {
            "appointment": appointment,
            "is_patient": is_patient,
            "notes": notes_qs,
            "form": form,
            "prescriptions": prescriptions,
            "files": files,
            "prescription_form": prescription_form,
            "file_form": file_form,
        },
    )


# ---------------------------
# CREAR / EDITAR CITA
# ---------------------------

@login_required
def appointment_create(request):
    if _is_patient(request.user):
        messages.error(request, "No tienes permiso para crear citas.")
        return redirect("my_appointments")

    if request.method == "POST":
        form = AppointmentForm(request.POST, doctor=request.user)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.doctor = request.user
            appt.save()
            messages.success(request, "Cita creada correctamente.")
            return redirect("appointment_detail", pk=appt.pk)
    else:
        form = AppointmentForm(doctor=request.user)

    return render(
        request,
        "appointments/appointment_form.html",
        {"form": form, "editing": False},
    )


@login_required
def appointment_edit(request, pk):
    if _is_patient(request.user):
        return redirect("my_appointments")

    appt = get_object_or_404(Appointment, pk=pk)

    if appt.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso para editar esta cita.")
        return redirect("doctor_agenda")

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appt, doctor=request.user)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.doctor = request.user
            appt.save()

            _safe_log_action(
                request,
                appointment=appt,
                action="UPDATE",
                object_type="Appointment",
                object_id=appt.id,
                message="Editó la cita",
            )

            messages.success(request, "Cita actualizada correctamente.")
            return redirect("appointment_detail", pk=appt.pk)

        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = AppointmentForm(instance=appt, doctor=request.user)

    return render(
        request,
        "appointments/appointment_form.html",
        {"form": form, "editing": True, "appt": appt},
    )


# ---------------------------
# CAMBIAR ESTADO (DOCTOR)
# (Backend queda, pero templates NO lo muestran)
# ---------------------------

@require_POST
@login_required
def appointment_set_status(request, pk, status):
    if _is_patient(request.user):
        return redirect("my_appointments")

    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    allowed = {"PENDING", "CONFIRMED", "CANCELLED", "DONE"}

    if status in allowed:
        appt.status = status
        appt.save()

        _safe_log_action(
            request,
            appointment=appt,
            action="STATUS",
            object_type="Appointment",
            object_id=appt.id,
            message=f"Cambió el estado a {status}",
        )

        messages.success(request, "Estado actualizado.")
    else:
        messages.error(request, "Estado inválido.")

    return redirect("appointment_detail", pk=appt.pk)


# ---------------------------
# DELETE: Prescriptions / Notes / Files
# ---------------------------

@require_POST
@login_required
def prescription_delete(request, pk, prescription_id):
    if _is_patient(request.user):
        messages.error(request, "No tienes permiso para hacer esto.")
        return redirect("appointment_detail", pk=pk)

    appointment = get_object_or_404(Appointment, pk=pk)

    if appointment.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso para eliminar recetas de esta cita.")
        return redirect("appointment_detail", pk=pk)

    prescription = get_object_or_404(
        Prescription, pk=prescription_id, appointment=appointment
    )
    prescription.delete()

    _safe_log_action(
        request,
        appointment=appointment,
        action="DELETE",
        object_type="Prescription",
        object_id=prescription_id,
        message="Eliminó un medicamento",
    )

    messages.success(request, "Medicamento eliminado correctamente.")
    return redirect("appointment_detail", pk=pk)


@require_POST
@login_required
def clinical_note_delete(request, pk, note_id):
    if _is_patient(request.user):
        messages.error(request, "No tienes permiso para hacer esto.")
        return redirect("appointment_detail", pk=pk)

    appointment = get_object_or_404(Appointment, pk=pk)

    if appointment.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso para eliminar notas de esta cita.")
        return redirect("appointment_detail", pk=pk)

    note = get_object_or_404(ClinicalNote, pk=note_id, appointment=appointment)
    note.delete()

    _safe_log_action(
        request,
        appointment=appointment,
        action="DELETE",
        object_type="ClinicalNote",
        object_id=note_id,
        message="Eliminó una nota clínica",
    )

    messages.success(request, "Nota clínica eliminada.")
    return redirect("appointment_detail", pk=pk)


@require_POST
@login_required
def appointment_file_delete(request, pk, file_id):
    if _is_patient(request.user):
        messages.error(request, "No tienes permiso para hacer esto.")
        return redirect("appointment_detail", pk=pk)

    appointment = get_object_or_404(Appointment, pk=pk)

    if appointment.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso para eliminar archivos de esta cita.")
        return redirect("appointment_detail", pk=pk)

    f = get_object_or_404(AppointmentFile, pk=file_id, appointment=appointment)

    if f.file:
        f.file.delete(save=False)
    f.delete()

    _safe_log_action(
        request,
        appointment=appointment,
        action="DELETE",
        object_type="AppointmentFile",
        object_id=file_id,
        message="Eliminó un archivo (Rayos X)",
    )

    messages.success(request, "Archivo eliminado.")
    return redirect("appointment_detail", pk=pk)


# ---------------------------
# PDF + EMAIL
# ---------------------------

@login_required
def appointment_prescriptions_pdf(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    is_patient = _is_patient(request.user)

    if is_patient and appointment.patient.user_id != request.user.id:
        messages.error(request, "No tienes permiso para descargar esta receta.")
        return redirect("my_appointments")

    if (not is_patient) and appointment.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso.")
        return redirect("doctor_agenda")

    pdf_bytes = build_prescriptions_pdf(appointment)

    _safe_log_action(
        request,
        appointment=appointment,
        action="PDF",
        object_type="Appointment",
        object_id=appointment.id,
        message="Descargó receta en PDF",
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="receta_cita_{appointment.id}.pdf"'
    )
    return response


@require_POST
@login_required
def appointment_prescriptions_email(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if _is_patient(request.user) or appointment.doctor_id != request.user.id:
        messages.error(request, "No tienes permiso para enviar esta receta.")
        return redirect("appointment_detail", pk=pk)

    patient_user = getattr(appointment.patient, "user", None)
    to_email = getattr(patient_user, "email", "") if patient_user else ""

    if not to_email:
        messages.error(request, "El paciente no tiene correo registrado.")
        return redirect("appointment_detail", pk=pk)

    pdf_bytes = build_prescriptions_pdf(appointment)

    subject = f"Receta médica - Cita #{appointment.id}"
    body = (
        f"Hola {appointment.patient},\n\n"
        f"Adjunto encontrarás la receta de tu cita #{appointment.id}.\n\n"
        "Saludos,\nClínica"
    )

    email = EmailMessage(subject=subject, body=body, to=[to_email])
    email.attach(f"receta_cita_{appointment.id}.pdf", pdf_bytes, "application/pdf")
    email.send(fail_silently=False)

    _safe_log_action(
        request,
        appointment=appointment,
        action="EMAIL",
        object_type="Appointment",
        object_id=appointment.id,
        message=f"Envió receta por correo a {to_email}",
    )

    messages.success(request, "Receta enviada por correo.")
    return redirect("appointment_detail", pk=pk)


# ---------------------------
# ACCIONES DEL PACIENTE
# ---------------------------

@require_POST
@login_required
def patient_confirm_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)

    if not _patient_can_touch(appt, request.user):
        messages.error(request, "No tienes permiso para confirmar esta cita.")
        return redirect("my_appointments")

    if appt.status in {"CANCELLED", "DONE"}:
        messages.error(request, "No puedes confirmar una cita cancelada o finalizada.")
        return redirect("appointment_detail", pk=pk)

    appt.status = "CONFIRMED"
    appt.save()
    messages.success(request, "Cita confirmada correctamente.")
    return redirect("appointment_detail", pk=pk)


@require_POST
@login_required
def patient_cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)

    if not _patient_can_touch(appt, request.user):
        messages.error(request, "No tienes permiso para cancelar esta cita.")
        return redirect("my_appointments")

    if appt.status in {"DONE"}:
        messages.error(request, "No puedes cancelar una cita finalizada.")
        return redirect("appointment_detail", pk=pk)

    appt.status = "CANCELLED"
    appt.save()
    messages.success(request, "Cita cancelada.")
    return redirect("appointment_detail", pk=pk)

@login_required
def patient_history(request):
    # Solo pacientes
    if not hasattr(request.user, "patient_profile"):
        return redirect("doctor_dashboard")

    patient = request.user.patient_profile
    now = timezone.now()

    # ---- filtros (GET) ----
    status = (request.GET.get("status") or "").upper().strip()
    q = (request.GET.get("q") or "").strip()
    date_from = parse_date(request.GET.get("from") or "")
    date_to = parse_date(request.GET.get("to") or "")

    allowed_status = {"PENDING", "CONFIRMED", "CANCELLED", "DONE"}

    qs = (
        Appointment.objects
        .filter(patient=patient, start_time__lt=now)  # solo pasadas
        .select_related("doctor")
        .prefetch_related("prescriptions")
        .annotate(rx_count=Count("prescriptions"))
        .order_by("-start_time")
    )

    if status in allowed_status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(reason__icontains=q)

    if date_from:
        qs = qs.filter(start_time__date__gte=date_from)

    if date_to:
        qs = qs.filter(start_time__date__lte=date_to)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "appointments/patient_history.html",
        {
            "page_obj": page_obj,
            "filters": {
                "status": status,
                "q": q,
                "from": request.GET.get("from", ""),
                "to": request.GET.get("to", ""),
            }
        },
    )

