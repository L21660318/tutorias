# apps/tutoring/models.py

from django.db import models
from django.conf import settings
from apps.academic.models import Career, Period
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class TutorGroup(models.Model):
    """
    Grupo de tutoría: lo maneja un tutor, pertenece a un período
    y opcionalmente a una carrera.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre del grupo")
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTOR'},
        related_name='tutor_groups'
    )
    period = models.ForeignKey(Period, on_delete=models.PROTECT, verbose_name="Período")
    career = models.ForeignKey(
        Career,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Carrera"
    )

    def __str__(self):
        return f"{self.name} - {self.tutor.get_full_name()} ({self.period})"



class TuteeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='tutee_profile'
    )
    career = models.ForeignKey(Career, on_delete=models.PROTECT, verbose_name="Carrera")

    # 🔹 ANTES:
    # assigned_tutor = models.ForeignKey(...)

    # 🔹 AHORA: pertenece a un grupo
    group = models.ForeignKey(
        TutorGroup,
        on_delete=models.PROTECT,
        related_name='tutees',
        verbose_name="Grupo de Tutoría",
        null=True,
        blank=True,
    )


    enrollment_id = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Promedio General")

    def __str__(self):
        return self.user.get_full_name()

    @property
    def assigned_tutor(self):
        # Para no romper lo demás: sigues pudiendo usar tutee_profile.assigned_tutor
        return self.group.tutor


class Session(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Programada"
        COMPLETED = "COMPLETED", "Realizada"
        CANCELED = "CANCELED", "Cancelada"
        NO_SHOW = "NO_SHOW", "Inasistencia"

    class Kind(models.TextChoices):
        PLAN = "PLAN", "Sesión del programa (12 PIT)"
        EXTRA = "EXTRA", "Sesión extra (solicitada)"

    # 🔹 Grupo al que pertenece la sesión (para las 12 planificadas)
    group = models.ForeignKey(
        TutorGroup,
        on_delete=models.PROTECT,
        related_name='sessions',
        null=True,
        blank=True,
        verbose_name="Grupo de Tutoría"
    )

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTOR'},
        related_name='tutor_sessions'
    )

    # 🔹 Para sesiones extra, o si después quieres registrar por alumno
    tutee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='tutee_sessions',
        null=True,
        blank=True,
        verbose_name="Tutorado (solo si es individual)"
    )

    period = models.ForeignKey(Period, on_delete=models.PROTECT, verbose_name="Período")

    kind = models.CharField(
        max_length=10,
        choices=Kind.choices,
        default=Kind.PLAN,
        verbose_name="Tipo de sesión"
    )

    activity_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de actividad (1-12)"
    )
    activity_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Título de la actividad"
    )
    activity_description = models.TextField(
        blank=True,
        verbose_name="Descripción / instrucciones de la actividad"
    )

    activity_material = models.FileField(
        upload_to="tutoring/activities/",
        null=True,
        blank=True,
        verbose_name="Material PDF"
    )

    scheduled_date = models.DateTimeField(verbose_name="Fecha y Hora Programada")
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.SCHEDULED)

    session_summary = models.TextField(blank=True, verbose_name="Resumen de la Sesión")
    agreements = models.TextField(blank=True, verbose_name="Acuerdos y Compromisos")

    def __str__(self):
        base = f"[{self.get_kind_display()}] {self.activity_number} - {self.activity_title}"
        if self.group:
            base += f" ({self.group.name})"
        return base
    

class SessionAttendance(models.Model):
    class AttendanceStatus(models.TextChoices):
        PRESENT = "PRESENT", "Asistió"
        ABSENT = "ABSENT", "No asistió"
        LATE = "LATE", "Llegó tarde"
        JUSTIFIED = "JUSTIFIED", "Falta justificada"

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    tutee = models.ForeignKey(
        TuteeProfile,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        verbose_name="Estado de asistencia"
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Observaciones"
    )

    class Meta:
        unique_together = ("session", "tutee")

    def __str__(self):
        return f"{self.session} - {self.tutee} ({self.get_status_display()})"

    
    
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
    
from django.db import models
from apps.users.models import User
from apps.academic.models import AcademicDepartment
from apps.academic.models import AcademicPeriod, AcademicCareer


class ActionProgram(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('in_review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('active', 'Activo'),
        ('completed', 'Completado'),
    ]
    department = models.ForeignKey(AcademicDepartment, on_delete=models.CASCADE)
    period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    objectives = models.TextField(blank=True, null=True)
    activities = models.TextField(blank=True, null=True)
    resources = models.TextField(blank=True, null=True)
    evaluation_metrics = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_actionprograms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TutorCoordinatorAssignment(models.Model):
    tutor = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='coordinator_assignment'
    )
    coordinator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutors_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asignación tutor-coordinador"
        verbose_name_plural = "Asignaciones tutor-coordinador"
        unique_together = ('tutor', 'coordinator')

    def clean(self):
            from django.core.exceptions import ValidationError

            if self.tutor and self.tutor.role != 'TUTOR':
                raise ValidationError(
                    {"tutor": "El usuario seleccionado como tutor no tiene el rol TUTOR."}
                )

            # aquí usamos COORDAC, que es lo que realmente guardas
            if self.coordinator and self.coordinator.role != 'COORDAC':
                raise ValidationError(
                    {"coordinator": "El usuario seleccionado como coordinador no tiene el rol COORDAC."}
                )

    def __str__(self):
        return f"{self.tutor} → {self.coordinator}"
    

# apps/tutoring/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class TutoringReport(models.Model):
    STATUS_CHOICES = [
        ('SENT', 'Enviado al coordinador'),
        ('REVIEWED', 'Revisado'),
        ('RETURNED', 'Devuelto al tutor'),
        ('SENT_TO_HEAD', 'Enviado al Jefe de Departamento'),
    ]

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutoring_reports'
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_tutoring_reports'
    )

    # Periodo del reporte
    period = models.CharField("Periodo", max_length=100)

    title = models.CharField("Título del reporte", max_length=200)
    content = models.TextField("Descripción / contenido del reporte")

    # ⬇⬇⬇ AQUÍ EL CAMBIO: Excel en lugar de PDF
    attachment = models.FileField(
        upload_to="tutoring/reports_excels/",
        null=True,
        blank=True,
        verbose_name="Archivo Excel",
        validators=[
            FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])
        ],
        help_text="Sube el archivo Excel del reporte (formato .xlsx o .xls)."
    )

    # 📝 Retroalimentación del coordinador
    feedback = models.TextField(
        "Retroalimentación del coordinador",
        blank=True
    )
    feedback_at = models.DateTimeField(
        "Fecha de retroalimentación",
        null=True,
        blank=True
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=STATUS_CHOICES,
        default='SENT'
    )

    sent_to_head_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reporte de tutoría"
        verbose_name_plural = "Reportes de tutoría"

    def __str__(self):
        return f"{self.title} - {self.tutor}"

    # -----------------------------
    # 🔍 Validaciones
    # -----------------------------
    def clean(self):
        super().clean()

        # Validar tutor
        if self.tutor_id and getattr(self.tutor, 'role', None) != 'TUTOR':
            raise ValidationError({
                "tutor": "El usuario seleccionado no tiene el rol TUTOR."
            })

        # Validar coordinador
        if self.coordinator_id and getattr(self.coordinator, 'role', None) != 'COORDAC':
            raise ValidationError({
                "coordinator": "El usuario seleccionado no tiene el rol COORDAC."
            })

    # -----------------------------
    # 💾 Guardado con asignación automática
    # -----------------------------
    def save(self, *args, **kwargs):
        # Import local para evitar errores de carga circular
        from apps.tutoring.models import TutorCoordinatorAssignment

        # Si no hay coordinador asignado, buscar el correspondiente al tutor
        if self.tutor_id and self.coordinator_id is None:
            assignment = TutorCoordinatorAssignment.objects.filter(
                tutor_id=self.tutor_id
            ).select_related('coordinator').first()

            if assignment:
                self.coordinator = assignment.coordinator

        super().save(*args, **kwargs)


class TutoringInterview(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Programada"
        COMPLETED = "COMPLETED", "Realizada"
        CANCELED = "CANCELED", "Cancelada"

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTOR'},
        related_name='interviews_as_tutor'
    )
    tutee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TUTEE'},
        related_name='interviews_as_tutee',
        verbose_name="Tutorado"
    )

    scheduled_date = models.DateTimeField("Fecha y hora de la entrevista")

    topic = models.CharField(
        "Tema / motivo de la entrevista",
        max_length=255,
        blank=True
    )

    summary = models.TextField(
        "Informe de la entrevista (lo hablado con el alumno)",
        blank=True
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Entrevista de tutoría"
        verbose_name_plural = "Entrevistas de tutoría"

    def __str__(self):
        return f"Entrevista con {self.tutee} ({self.scheduled_date:%d/%m/%Y %H:%M})"
    




from django.db import models
from django.conf import settings
from apps.academic.models import Period

class TutorCompliance(models.Model):
    STATUS_CHOICES = [
        ("COMPLIED", "Cumplió con los objetivos"),
        ("NOT_COMPLIED", "No cumplió con los objetivos"),
    ]

    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_compliances",
    )
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="compliance_records",
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="tutor_compliances",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("coordinator", "tutor", "period")

    def __str__(self):
        return f"{self.tutor} - {self.period} - {self.get_status_display()}"

from django.conf import settings
from django.db import models
from apps.academic.models import Period


class TutorComplianceReport(models.Model):
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_compliance_reports",
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="tutor_compliance_reports",
    )
    pdf = models.FileField(
        upload_to="tutor_compliance_reports/"
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("coordinator", "period")

    def __str__(self):
        return f"Reporte {self.coordinator} - {self.period}"