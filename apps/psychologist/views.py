from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import PsychologySession
from apps.tutoring.models import TuteeProfile
from .forms import PsychologySessionAssignForm, PsychologySessionScheduleForm


def dashboard_view(request):
    # Si alguien entra a /psychologist/ lo mandamos al dashboard real
    return psychologist_dashboard(request)


@login_required
def assign_student_psychologist(request):
    # Quien puede canalizar (ajusta según tus roles)
    if getattr(request.user, "role", None) not in ("TUTOR", "COORDAC", "JEFEDEPTO") and not request.user.is_superuser:
        return redirect("/")

    if request.method == "POST":
        form = PsychologySessionAssignForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            # El tutor canaliza, el psicólogo luego define fecha/hora
            session.is_confidential = True
            # Opcional: aseguramos que no tenga fecha/hora al crear
            session.session_date = None
            session.session_time = None
            session.save()
            messages.success(
                request,
                "Estudiante canalizado a psicología correctamente. "
                "El psicólogo asignado definirá fecha y hora de la sesión."
            )
            return redirect("tutoring")
    else:
        form = PsychologySessionAssignForm()

    return render(request, "psychologist/assign_student.html", {"form": form})


@login_required
def psychologist_dashboard(request):
    # Opcional: restringir a usuarios con rol psicólogo
    if getattr(request.user, "role", None) != "PSYCHOLOGIST" and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder al módulo de Psicología.")
        return redirect("/")

    # 1) Todas las sesiones donde el usuario logueado es el psicólogo
    sessions_qs = (
        PsychologySession.objects
        .filter(psychologist_id=request.user.id)
        .select_related("student__user", "student__career")
        .order_by("-session_date", "-created_at")
    )

    # 2) IDs de TuteeProfile asignados a este psicólogo
    student_ids = sessions_qs.values_list("student_id", flat=True).distinct()

    # 3) Estudiantes asignados
    assigned_students = (
        TuteeProfile.objects
        .filter(id__in=student_ids)
        .select_related("user", "career")
        .order_by("user__first_name", "user__last_name")
    )

    # 4) Stats rápidas
    students_count = assigned_students.count()
    sessions_count = sessions_qs.count()
    priority_cases = (
        sessions_qs
        .filter(risk_level="high")
        .values("student_id")
        .distinct()
        .count()
    )
    pending_schedule = (
        sessions_qs
        .filter(session_date__isnull=True)
        .values("student_id")
        .distinct()
        .count()
    )

    # 5) Próximas sesiones (solo las que ya tienen fecha)
    upcoming_sessions = (
        sessions_qs
        .filter(session_date__isnull=False)
        .order_by("session_date", "session_time")[:5]
    )

    # 6) Sesiones pendientes de programar (sin fecha)
    pending_sessions = (
        sessions_qs
        .filter(session_date__isnull=True)
        .order_by("created_at")
    )

    context = {
        "stats": {
            "students_count": students_count,
            "sessions_count": sessions_count,
            "priority_cases": priority_cases,
            "pending_schedule": pending_schedule,
        },
        "assigned_students": assigned_students,
        "upcoming_sessions": upcoming_sessions,
        "pending_sessions": pending_sessions,
    }

    return render(request, "psychologist/dashboard.html", context)


@login_required
def schedule_session(request, pk):
    """Vista para que el psicólogo asigne fecha y hora a una sesión."""
    if getattr(request.user, "role", None) != "PSYCHOLOGIST" and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para programar sesiones.")
        return redirect("/")

    session = get_object_or_404(
        PsychologySession,
        pk=pk,
        psychologist_id=request.user.id,  # solo sus sesiones
    )

    if request.method == "POST":
        form = PsychologySessionScheduleForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Sesión programada correctamente.")
            return redirect("psychologist_dashboard")
    else:
        form = PsychologySessionScheduleForm(instance=session)

    return render(
        request,
        "psychologist/schedule_session.html",
        {"form": form, "session": session},
    )
