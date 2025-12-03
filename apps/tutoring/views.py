# apps/tutoring/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .forms import SessionForm

from .models import Session, Alert, TuteeProfile, SessionAttendance
from apps.academic.models import Period

from .models import TutoringReport, TutorCoordinatorAssignment
from .forms import TutoringReportForm
from django.contrib.auth import get_user_model

User = get_user_model()


def is_tutor(user):
    return getattr(user, 'role', None) == 'TUTOR'


def is_coordac(user):
    return getattr(user, 'role', None) == 'COORDAC'

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
    #   Antes: assigned_tutor=user  → ahora se usa la relación group__tutor
    students_count = (
        TuteeProfile.objects
        .filter(group__tutor=user)
        .distinct()
        .count()
    )

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
    # Antes: tutee__tutee_profile__assigned_tutor=user
    alerts_count = Alert.objects.filter(
        tutee__tutee_profile__group__tutor=user,
        is_resolved=False,
    ).distinct().count()

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

            # --- Regla 1: máximo 12 sesiones por tutorado y período ---
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


@login_required
def tutoring_session_detail(request, pk):
    """
    Vista para que el tutor abra una sesión, vea el grupo y pase lista.
    """
    user = request.user

    # Solo tutores (o staff) pueden entrar
    if getattr(user, "role", None) != "TUTOR" and not user.is_staff:
        messages.error(request, "No tienes permisos para acceder a esta sesión.")
        return redirect("/")

    session = get_object_or_404(Session, pk=pk, tutor=user)

    if not session.group:
        messages.error(request, "Esta sesión no tiene un grupo asociado.")
        return redirect("/tutoring/")

    group = session.group

    # Alumnos del grupo
    students = (
        TuteeProfile.objects
        .filter(group=group)
        .select_related("user", "career")
        .order_by("user__last_name", "user__first_name")
    )

    # Asistencias ya registradas (para prellenar)
    existing_attendance = {
        att.tutee_id: att.status
        for att in SessionAttendance.objects.filter(session=session)
    }

    if request.method == "POST":
        for t in students:
            status_value = request.POST.get(f"status_{t.id}")
            notes_value = request.POST.get(f"notes_{t.id}", "").strip()

            if not status_value:
                continue

            attendance, created = SessionAttendance.objects.get_or_create(
                session=session,
                tutee=t,
            )
            attendance.status = status_value
            attendance.notes = notes_value
            attendance.save()

        # marcar la sesión como realizada
        session.status = Session.Status.COMPLETED
        session.save()

        messages.success(request, "Asistencia guardada correctamente.")
        return redirect("tutoring")

    context = {
        "session": session,
        "group": group,
        "students": students,
        "existing_attendance": existing_attendance,
    }
    return render(request, "tutoring/session_detail.html", context)

@login_required
def tutor_report_create(request):
    if not is_tutor(request.user):
        messages.error(request, "No tienes permisos para generar reportes de tutoría.")
        return redirect('home')

    # Buscamos su coordinador asignado
    assignment = TutorCoordinatorAssignment.objects.filter(
        tutor=request.user
    ).select_related('coordinator').first()

    if not assignment:
        messages.warning(
            request,
            "Aún no tienes un coordinador asignado. El reporte se guardará sin destinatario hasta que el Jefe de Departamento te asigne uno."
        )

    if request.method == 'POST':
        form = TutoringReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.tutor = request.user
            # El save() del modelo intentará asignar coordinator automáticamente
            report.status = 'SENT'
            report.save()
            messages.success(
                request,
                "El reporte ha sido generado y enviado al coordinador asignado."
            )
            return redirect('tutor_report_list')
    else:
        form = TutoringReportForm()

    context = {
        'form': form,
        'assignment': assignment,
    }
    return render(request, 'tutoring/tutor_report_form.html', context)


@login_required
def tutor_report_list(request):
    if not is_tutor(request.user):
        messages.error(request, "No tienes permisos para ver estos reportes.")
        return redirect('home')

    reports = TutoringReport.objects.filter(tutor=request.user).select_related('coordinator')
    return render(request, 'tutoring/tutor_report_list.html', {
        'reports': reports,
    })


@login_required
def coordinator_report_inbox(request):
    if not is_coordac(request.user):
        messages.error(request, "Solo los coordinadores académicos pueden ver esta sección.")
        return redirect('home')

    reports = TutoringReport.objects.filter(
        coordinator=request.user
    ).select_related('tutor')

    return render(request, 'tutoring/coordinator_report_inbox.html', {
        'reports': reports,
    })
