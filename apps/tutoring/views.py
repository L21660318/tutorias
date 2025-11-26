# apps/tutoring/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .forms import SessionForm


from .models import Session, Alert, TuteeProfile


@login_required
def dashboard_view(request):
    # Solo TUTOR (o admin)
    if getattr(request.user, "role", None) != "TUTOR" and not request.user.is_superuser:
        return redirect("/")

    user = request.user
    now = timezone.now()
    first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Todas las SESIONES donde él es tutor
    sessions = Session.objects.filter(tutor=user)

    # === TARJETAS ===

    # 1) Número de tutorados asignados a este tutor (aunque aún no tengan sesiones)
    students_count = TuteeProfile.objects.filter(
        assigned_tutor=user
    ).count()

    # 2) Número de tutores activos: usuarios que aparecen como tutor en alguna sesión
    tutors_count = Session.objects.values("tutor").distinct().count()

    # 3) Sesiones de este mes (según fecha programada)
    sessions_this_month = sessions.filter(
        scheduled_date__gte=first_day_month,
        scheduled_date__month=now.month,
        scheduled_date__year=now.year,
    ).count()

    # 4) Progreso del programa: % de sesiones COMPLETED vs totales del tutor
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(status=Session.Status.COMPLETED).count()
    program_progress = 0
    if total_sessions > 0:
        program_progress = round((completed_sessions / total_sessions) * 100)

    # Actividades recientes (últimas sesiones del tutor)
    recent_sessions = (
        sessions
        .select_related("tutor", "tutee", "period")
        .order_by("-scheduled_date")[:10]
    )

    # Alertas NO resueltas para sus tutorados
    alerts_count = Alert.objects.filter(
        tutee__tutee_profile__assigned_tutor=user,
        is_resolved=False,
    ).count()

    context = {
        "stats": {
            "students_count": students_count,
            "tutors_count": tutors_count,
            "sessions_this_month": sessions_this_month,
            "program_progress": program_progress,
        },
        "recent_sessions": recent_sessions,
        "alerts_count": alerts_count,
    }
    return render(request, "tutoring/dashboard.html", context)


@login_required
def create_session(request):
    # Solo TUTOR (o admin)
    if getattr(request.user, "role", None) != "TUTOR" and not request.user.is_superuser:
        return redirect("/")

    if request.method == "POST":
        form = SessionForm(request.POST, tutor=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.tutor = request.user

            tutee = session.tutee
            period = session.period
            sd = session.scheduled_date

            # --- Regla 1: máximo 12 sesiones por tutorado y periodo ---
            total_period = Session.objects.filter(
                tutor=request.user,
                tutee=tutee,
                period=period,
            ).count()

            if total_period >= 12:
                form.add_error(
                    None,
                    "Este tutorado ya tiene 12 sesiones programadas en este período."
                )
            else:
                # --- Regla 2: máximo 2 sesiones por mes por tutorado (programadas por el tutor) ---
                month_start = sd.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # calcular inicio del siguiente mes
                if month_start.month == 12:
                    next_month_start = month_start.replace(year=month_start.year + 1, month=1)
                else:
                    next_month_start = month_start.replace(month=month_start.month + 1)

                monthly_count = Session.objects.filter(
                    tutor=request.user,
                    tutee=tutee,
                    scheduled_date__gte=month_start,
                    scheduled_date__lt=next_month_start,
                ).count()

                if monthly_count >= 2:
                    form.add_error(
                        None,
                        "Ya tienes 2 sesiones programadas este mes con este tutorado. "
                        "Las demás deberán ser solicitadas como sesiones extra por el estudiante."
                    )
                else:
                    session.status = Session.Status.SCHEDULED
                    session.save()
                    messages.success(request, "Sesión programada correctamente.")
                    return redirect("tutoring")
    else:
        form = SessionForm(tutor=request.user)

    return render(request, "tutoring/session_form.html", {"form": form})