# apps/academic/models.py

from django.db import models

class Period(models.Model):
    """
    Representa un período académico, ej. "2025-1".
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="¿Está activo?")

    def __str__(self):
        return self.name

class Career(models.Model):
    """
    Representa una carrera o programa educativo.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Nombre de la Carrera")
    abbreviation = models.CharField(max_length=20, blank=True, verbose_name="Abreviatura")

    def __str__(self):
        return self.name