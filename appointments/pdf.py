from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_prescriptions_pdf(appointment):
    """
    Retorna bytes del PDF con las recetas de una cita.
    Requiere ReportLab: pip install reportlab
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Receta médica - Cita #{appointment.id}")
    y -= 22

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Paciente: {appointment.patient}")
    y -= 16
    c.drawString(50, y, f"Fecha: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Medicamentos:")
    y -= 18

    c.setFont("Helvetica", 10)

    prescriptions = appointment.prescriptions.all().order_by("-created_at")

    if not prescriptions:
        c.drawString(60, y, "No hay medicamentos registrados.")
        y -= 14
    else:
        for p in prescriptions:
            # Ajusta aquí a tus campos reales:
            med = getattr(p, "medication", "") or getattr(p, "medicine", "") or "—"
            dosage = getattr(p, "dosage", "") or getattr(p, "dose", "") or "—"
            freq = getattr(p, "frequency", "") or "—"
            dur = getattr(p, "duration", "") or "—"

            c.drawString(60, y, f"- {med}")
            y -= 14
            c.drawString(80, y, f"Dosis: {dosage} | Frecuencia: {freq} | Duración: {dur}")
            y -= 18

            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
