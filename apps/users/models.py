# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de Usuario personalizado para diferenciar roles.
    """
    class Role(models.TextChoices):
        TUTOR = "TUTOR", "Tutor"
        TUTEE = "TUTEE", "Tutorado"
        SUBDIRECTORAC = "SUBAC", "Subdirección Académica"
        COORDAC = "COORDAC", "Coordinación Académica"
        COORDINST = "COORDINST", "Coordinación Institucional"
        JEFEDEPTO = "JEFEDEPTO", "Jefe de Departamento Académico"
        JEFEDEPTODES = "JEFEDEPTODES", "Jefe de Departamento de Desarrollo"

    # El username, password, email, etc., ya vienen con AbstractUser
    role = models.CharField(max_length=50, choices=Role.choices)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"