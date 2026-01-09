from django.utils import timezone

def log_action(user, action, appointment=None):
    """
    Registro simple de acciones (puedes ampliarlo luego)
    """
    print(
        f"[{timezone.now()}] {user} -> {action}"
        + (f" | cita #{appointment.id}" if appointment else "")
    )
