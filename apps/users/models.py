# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de Usuario personalizado para diferenciar roles y permitir imagen de perfil.
    """
    class Role(models.TextChoices):
        TUTOR = "TUTOR", "Tutor"
        TUTEE = "TUTEE", "Tutorado"
        SUBDIRECTORAC = "SUBAC", "Subdirección Académica"
        COORDAC = "COORDAC", "Coordinación Académica"
        COORDINST = "COORDINST", "Coordinación Institucional"
        JEFEDEPTO = "JEFEDEPTO", "Jefe de Departamento Académico"
        JEFEDEPTODES = "JEFEDEPTODES", "Jefe de Departamento de Desarrollo"
        PSYCHOLOGIST = "PSYCHOLOGIST", "Psicólogo"

    role = models.CharField(max_length=50, choices=Role.choices, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        full_name = self.get_full_name() or self.username
        role_display = self.get_role_display() if self.role else "Sin rol"
        return f"{full_name} ({role_display})"
