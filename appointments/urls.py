from django.urls import path
from . import views

urlpatterns = [
    path("my/", views.my_appointments, name="my_appointments"),
    path("agenda/", views.doctor_agenda, name="doctor_agenda"),
    path("dashboard/", views.doctor_dashboard, name="doctor_dashboard"),


    path("create/", views.appointment_create, name="appointment_create"),
    path("<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("<int:pk>/edit/", views.appointment_edit, name="appointment_edit"),
    path("history/", views.patient_history, name="patient_history"),


    path("<int:pk>/status/<str:status>/", views.appointment_set_status, name="appointment_set_status"),

    path("<int:pk>/prescriptions/pdf/", views.appointment_prescriptions_pdf, name="appointment_prescriptions_pdf"),
    path("<int:pk>/prescriptions/email/", views.appointment_prescriptions_email, name="appointment_prescriptions_email"),

    path("<int:pk>/notes/<int:note_id>/delete/", views.clinical_note_delete, name="clinical_note_delete"),
    path("<int:pk>/prescriptions/<int:prescription_id>/delete/", views.prescription_delete, name="prescription_delete"),
    path("<int:pk>/files/<int:file_id>/delete/", views.appointment_file_delete, name="appointment_file_delete"),

    # ✅ ACCIONES PACIENTE
    path("<int:pk>/patient/confirm/", views.patient_confirm_appointment, name="patient_confirm_appointment"),
    path("<int:pk>/patient/cancel/", views.patient_cancel_appointment, name="patient_cancel_appointment"),
    
]
