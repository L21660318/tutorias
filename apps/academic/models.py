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
    
from apps.users.models import User


class AcademicDepartment(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DepartmentCoordinator(models.Model):
    department = models.ForeignKey(AcademicDepartment, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AcademicPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AcademicCareer(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey('academic.AcademicDepartment', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name