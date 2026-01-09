from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import Appointment

@shared_task
def send_confirmations_24h():
    now = timezone.now()
    start = now + timedelta(hours=24)
    end = now + timedelta(hours=25)

    qs = Appointment.objects.filter(
        status__in=["PENDING", "CONFIRMED"],
        start_time__range=(start, end),
    ).select_related("patient__user")

    for appt in qs:
        email = appt.patient.user.email
        if not email:
            continue
        send_mail(
            subject="Confirmación de cita",
            message=f"Hola {appt.patient}. Tu cita es el {appt.start_time}. Responde para confirmar.",
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )
