# apps/academic/admin.py

from django.contrib import admin
from .models import Career, Period, AcademicDepartment, AcademicPeriod, AcademicCareer  # ajusta según tus modelos reales


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name",)


@admin.register(AcademicDepartment)
class AcademicDepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name",)


@admin.register(AcademicCareer)
class AcademicCareerAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    search_fields = ("name",)
