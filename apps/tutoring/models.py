# apps/tutoring/models.py

from django.db import models
from django.conf import settings
from apps.academic.models import Career, Period

class TuteeProfile(models.Model):
    """
    Ficha del Tutorado. Contiene información adicional del usuario tutorado.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='tutee_profile'
    )
    career = models.ForeignKey(Career, on_delete=models.PROTECT, verbose_name="Carrera")
    assigned_tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'TUTOR'},
        related_name='assigned_tutees',
        verbose_name="Tutor Asignado"
    )
    enrollment_id = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Promedio General")

    def __str__(self):
        return self.user.get_full_name()

class Session(models.Model):
    """
    Agenda y Bitácora de una sesión de tutoría.
    """
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Programada"
        COMPLETED = "COMPLETED", "Realizada"
        CANCELED = "CANCELED", "Cancelada"
        NO_SHOW = "NO_SHOW", "Inasistencia"

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTOR'},
        related_name='tutor_sessions'
    )
    tutee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='tutee_sessions'
    )
    period = models.ForeignKey(Period, on_delete=models.PROTECT, verbose_name="Período")
    scheduled_date = models.DateTimeField(verbose_name="Fecha y Hora Programada")
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.SCHEDULED)
    
    # Campos para la bitácora
    session_summary = models.TextField(blank=True, verbose_name="Resumen de la Sesión")
    agreements = models.TextField(blank=True, verbose_name="Acuerdos y Compromisos")

    def __str__(self):
        return f"Sesión de {self.tutor.first_name} con {self.tutee.first_name} - {self.scheduled_date.strftime('%Y-%m-%d')}"

class Alert(models.Model):
    """
    Alerta temprana generada para un tutorado.
    """
    class AlertType(models.TextChoices):
        ABSENCE = "ABSENCE", "Inasistencia Reiterada"
        LOW_PERFORMANCE = "LOW_PERFORMANCE", "Bajo Rendimiento Académico"
        OTHER = "OTHER", "Otro Motivo"

    tutee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=50, choices=AlertType.choices)
    description = models.TextField(verbose_name="Descripción de la Alerta")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, verbose_name="¿Atendida?")

    def __str__(self):
        return f"Alerta para {self.tutee.get_full_name()} ({self.get_alert_type_display()})"

class InterventionGuide(models.Model):
    """
    Guías de intervención para los tutores.
    """
    title = models.CharField(max_length=255, verbose_name="Título")
    content = models.TextField(verbose_name="Contenido de la Guía")
    # Opcional: relacionar guías a tipos de alertas o carreras
    # alert_type_related = models.CharField(max_length=50, choices=Alert.AlertType.choices, blank=True, null=True)

    def __str__(self):
        return self.title