# apps/tutee/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.tutoring.models import TuteeProfile, Session, Alert, TutorGroup
from apps.academic.models import Period
from apps.psychologist.models import PsychologySession  # 👈 IMPORTANTE


@login_required
def tutee_dashboard(request):
    user = request.user

    # 1. Verificamos que tenga perfil de tutorado
    try:
        tutee_profile = user.tutee_profile
    except TuteeProfile.DoesNotExist:
        # Si no tiene perfil, lo mando al dashboard general
        return redirect('tutoring')

    group = tutee_profile.group  # campo que ya agregamos al modelo
    tutor = group.tutor if group else None

    # 2. Período actual (ajusta esto según tu modelo Period)
    current_period = (
        Period.objects.filter(is_active=True).first()
        or Period.objects.order_by('-id').first()
    )

    now = timezone.now()

    # 3. Sesiones del programa (las 12) asociadas al grupo
    base_qs = Session.objects.filter(
        group=group,
        period=current_period,
        kind=Session.Kind.PLAN
    ).order_by('scheduled_date')

    upcoming_qs = base_qs.filter(
        scheduled_date__gte=now
    ).order_by('scheduled_date')[:3]

    recent_qs = base_qs.filter(
        scheduled_date__lt=now,
        status=Session.Status.COMPLETED
    ).order_by('-scheduled_date')[:4]

    # 4. Mapeo a lo que tu template espera (upcoming_sessions) — TUTORÍA
    upcoming_sessions = []
    for s in upcoming_qs:
        upcoming_sessions.append({
            "type": "Sesión del programa",
            "label": s.get_status_display(),
            "date": s.scheduled_date.strftime("%d/%m/%Y"),
            "time": s.scheduled_date.strftime("%H:%M"),
            "place": getattr(s, "location", "Por definir"),  # si luego agregas campo location
            "topic": s.activity_title or "Sin tema",
            "can_reschedule": True,  # aquí luego metes tu regla de negocio
        })

    # 5. Mapeo a lo que tu template espera (recent_sessions) — TUTORÍA
    recent_sessions = []
    for s in recent_qs:
        recent_sessions.append({
            "type": "Sesión del programa",
            "date": s.scheduled_date.strftime("%d/%m/%Y"),
            "topic": s.activity_title or "Sin tema",
            # por ahora asumimos que COMPLETED = asistió
            "attended": s.status == Session.Status.COMPLETED,
            "feedback_sent": False,  # luego lo ligas con un modelo de feedback
        })

    # ============================
    # 6. SESIONES DE PSICOLOGÍA
    # ============================
    today = timezone.localdate()

    psych_qs = (
        PsychologySession.objects
        .filter(student=tutee_profile, session_date__isnull=False)
        .order_by("session_date", "session_time")
    )

    psych_upcoming_qs = psych_qs.filter(session_date__gte=today)
    psych_recent_qs = psych_qs.filter(session_date__lt=today).order_by(
        "-session_date", "-session_time"
    )[:4]

    # Próximas sesiones de PSICOLOGÍA → se añaden a upcoming_sessions
    for ps in psych_upcoming_qs:
        upcoming_sessions.append({
            "type": "Sesión con Psicología",
            "label": "Psicología",
            "date": ps.session_date.strftime("%d/%m/%Y") if ps.session_date else "Sin fecha",
            "time": ps.session_time.strftime("%H:%M") if ps.session_time else "",
            "place": "Departamento de Psicología",
            "topic": ps.reason or "Sin motivo registrado",
            "can_reschedule": True,
        })

    # Sesiones recientes de PSICOLOGÍA → se añaden a recent_sessions
    for ps in psych_recent_qs:
        recent_sessions.append({
            "type": "Sesión con Psicología",
            "date": ps.session_date.strftime("%d/%m/%Y") if ps.session_date else "",
            "topic": ps.reason or "Sin motivo registrado",
            "attended": True,      # luego lo ligas con algún campo real
            "feedback_sent": False  # idem
        })

    # 7. Stats básicas del programa (solo tutoría, por ahora)
    total_program_sessions = base_qs.count()
    completed_program_sessions = base_qs.filter(
        status=Session.Status.COMPLETED
    ).count()

    attendance_percent = int(
        completed_program_sessions * 100 / total_program_sessions
    ) if total_program_sessions else 0

    stats = {
        "sessions_programmed": total_program_sessions,
        "sessions_completed": completed_program_sessions,
        "attendance_percent": attendance_percent,
        "feedback_sent": 0,                          # futuro: contar feedback real
        "feedback_expected": total_program_sessions, # 1 feedback por sesión
        "program_progress_percent": attendance_percent,
    }

    # 8. Datos del estudiante (lo que usa tu template)
    credits_required = 5           # ajusta según tu reglamento
    credits_obtained = 2           # aquí luego conectas a un modelo real
    credits_progress_percent = int(
        credits_obtained * 100 / credits_required
    ) if credits_required else 0

    student = {
        "full_name": tutee_profile.user.get_full_name() or tutee_profile.user.username,
        "career": tutee_profile.career.name if tutee_profile.career else "",
        "semester": "",  # si después agregas campo semestre al perfil, lo pones aquí
        "matricula": tutee_profile.enrollment_id,
        "credits_obtained": credits_obtained,
        "credits_required": credits_required,
        "credits_progress_percent": credits_progress_percent,
    }

    # 9. Datos del tutor (lo que tu template ya pinta)
    if tutor:
        department_name = getattr(
            getattr(tutor, "department", None), "name", ""
        )
        specialty = getattr(tutor, "specialty", "")
        tutor_email = tutor.email
        tutor_full_name = tutor.get_full_name() or tutor.username
    else:
        department_name = ""
        specialty = ""
        tutor_email = ""
        tutor_full_name = "Sin tutor asignado"

    tutor_info = {
        "full_name": tutor_full_name,
        "department": department_name,
        "specialty": specialty,
        "email": tutor_email,
    }

    # 10. Notificaciones simples: alertas + próximas sesiones (tutoría + psicología)
    alerts = Alert.objects.filter(tutee=user, is_resolved=False)
    notifications = []

    for a in alerts:
        notifications.append(
            f"Alerta: {a.get_alert_type_display()} - {a.description[:50]}..."
        )

    # Sesiones de TUTORÍA
    for s in upcoming_qs:
        notifications.append(
            f"Sesión de tutoría el {s.scheduled_date.strftime('%d/%m/%Y %H:%M')} - {s.activity_title or 'Sesión del programa'}"
        )

    # Sesiones de PSICOLOGÍA
    for ps in psych_upcoming_qs:
        fecha = ps.session_date.strftime('%d/%m/%Y') if ps.session_date else 'Sin fecha'
        hora = ps.session_time.strftime('%H:%M') if ps.session_time else ''
        notifications.append(
            f"Sesión con Psicología el {fecha} {hora} - {ps.reason[:40] if ps.reason else 'Sesión psicológica'}"
        )

    context = {
        "student": student,
        "tutor": tutor_info,
        "stats": stats,
        "upcoming_sessions": upcoming_sessions,
        "recent_sessions": recent_sessions,
        "notifications": notifications[:5],  # top 5
    }

    return render(request, "tutee/dashboard.html", context)


@login_required
def tutee_activities_view(request):
    user = request.user

    # Verificar que tenga perfil de tutorado
    try:
        tutee_profile = user.tutee_profile
    except TuteeProfile.DoesNotExist:
        return redirect('tutoring')

    group = tutee_profile.group
    if not group:
        return render(request, "tutee/activities.html", {
            "student_name": user.get_full_name() or user.username,
            "activities": [],
            "has_group": False,
        })

    # Período actual (ajusta al modelo que tienes)
    current_period = (
        Period.objects.filter(is_active=True).first()
        or Period.objects.order_by('-id').first()
    )

    # Actividades del programa (12) + extras ligadas al grupo
    activities_qs = Session.objects.filter(
        group=group,
        period=current_period,
    ).order_by('scheduled_date')

    context = {
        "student_name": user.get_full_name() or user.username,
        "group": group,
        "activities": activities_qs,
        "has_group": True,
    }

    return render(request, "tutee/activities.html", context)
