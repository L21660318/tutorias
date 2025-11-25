from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group

@login_required
def tutee_dashboard(request):
    # Opcional: asegurar que solo usuarios del grupo TUTEE entren aquí
    #if not request.user.groups.filter(name__iexact='TUTEE').exists() and not request.user.is_superuser:
       #return redirect('/')  # o a otra vista si quieres

    user = request.user

    student_data = {
        "full_name": user.get_full_name() or user.username,
        "career": "Ingeniería en Sistemas Computacionales",
        "semester": "3er Semestre",
        "matricula": "202345678",
        "credits_obtained": 2,
        "credits_required": 5,
        "credits_progress_percent": 40,
    }

    tutor_data = {
        "full_name": "Dr. Juan Carlos Martínez",
        "department": "Sistemas y Computación",
        "specialty": "Inteligencia Artificial",
        "email": "jmartinez@tecnm.mx",
    }

    stats = {
        "sessions_completed": 8,
        "sessions_programmed": 12,
        "attendance_percent": 92,
        "feedback_sent": 6,
        "program_progress_percent": 67,
        "feedback_expected": 8,
    }

    upcoming_sessions = [
        {
            "type": "Sesión Individual",
            "label": "Próxima",
            "date": "Lunes, 20 de Octubre 2025",
            "time": "14:00 - 15:00 hrs",
            "place": "Oficina de Tutorías - Edificio B",
            "topic": "Avance en proyecto de bases de datos",
            "can_reschedule": True,
        },
        {
            "type": "Sesión Grupal",
            "label": "Grupal",
            "date": "Viernes, 24 de Octubre 2025",
            "time": "16:00 - 17:30 hrs",
            "place": "Aula 204 - Edificio Principal",
            "topic": "Técnicas de estudio y preparación para exámenes",
            "can_reschedule": False,
        },
    ]

    recent_sessions = [
        {
            "type": "Sesión Individual",
            "date": "Miércoles, 15 de Octubre 2025",
            "topic": "Revisión de avance académico",
            "attended": True,
            "feedback_sent": False,
        },
        {
            "type": "Sesión Grupal",
            "date": "Viernes, 10 de Octubre 2025",
            "topic": "Manejo del estrés académico",
            "attended": True,
            "feedback_sent": True,
        },
    ]

    notifications = [
        "Nueva sesión programada para mañana",
        "Recordatorio: Encuesta de satisfacción pendiente",
        "Tu tutor ha enviado un mensaje",
    ]

    context = {
        "student": student_data,
        "tutor": tutor_data,
        "stats": stats,
        "upcoming_sessions": upcoming_sessions,
        "recent_sessions": recent_sessions,
        "notifications": notifications,
    }

    return render(request, "tutee/dashboard.html", context)
