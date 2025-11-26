# apps/tutoring/admin.py

from django.contrib import admin
from .models import TuteeProfile, Session, Alert, InterventionGuide, ActionProgram


@admin.register(TuteeProfile)
class TuteeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "career", "assigned_tutor", "enrollment_id", "current_gpa")
    search_fields = ("user__username", "user__first_name", "user__last_name", "enrollment_id")
    list_filter = ("career", "assigned_tutor")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("scheduled_date", "tutor", "tutee", "period", "status")
    list_filter = ("status", "period", "tutor")
    search_fields = (
        "tutor__first_name", "tutor__last_name",
        "tutee__first_name", "tutee__last_name",
    )
    ordering = ("-scheduled_date",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("tutee", "alert_type", "created_at", "is_resolved")
    list_filter = ("alert_type", "is_resolved")
    search_fields = ("tutee__first_name", "tutee__last_name")


@admin.register(InterventionGuide)
class InterventionGuideAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(ActionProgram)
class ActionProgramAdmin(admin.ModelAdmin):
    list_display = ("department", "period", "status", "created_by", "created_at")
    list_filter = ("status", "department", "period")
    search_fields = ("department__name", "created_by__username")

