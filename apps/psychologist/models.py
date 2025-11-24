from django.db import models
from apps.users.models import User
from apps.tutoring.models import TuteeProfile
from apps.academic.models import AcademicPeriod, AcademicCareer

class PsychologySession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Grupal'),
        ('urgent', 'Urgente'),
        ('followup', 'Seguimiento'),
    ]
    PERFORMANCE_LEVELS = [
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('regular', 'Regular'),
        ('low', 'Bajo'),
        ('critical', 'Crítico'),
    ]
    RISK_LEVELS = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ]

    student = models.ForeignKey(TuteeProfile, on_delete=models.CASCADE)
    session_date = models.DateField()
    session_time = models.TimeField()
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='individual')
    reason = models.TextField()
    observations = models.TextField(blank=True, null=True)
    performance_level = models.CharField(max_length=10, choices=PERFORMANCE_LEVELS, default='regular')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    is_confidential = models.BooleanField(default=True)
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
