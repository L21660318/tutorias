from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def coordac_view(request):
    # Si tu User tiene relación con departamento, por ejemplo user.department
    department = getattr(request.user, "department", None)

    # Notificaciones de ejemplo (cámbialas luego por query a tu modelo)
    notifications = [
        {"text": "Diagnóstico institucional recibido", "url": "#"},
        {"text": "3 solicitudes de cambio de tutor pendientes", "url": "#"},
        {"text": "Evaluación departamental próxima", "url": "#"},
        {"text": "Recordatorio: Envío de lista de formación", "url": "#"},
    ]

    dept_stats = {
        "tutors_active": 18,
        "tutors_certified": 15,
        "students_served": 320,
        "coverage": "85%",
        "pat_compliance": "92%",
        "pat_variation": "+5%",
        "pending_changes": 3,
        "tutors_designation_progress": 80,
    }

    context = {
        # Datos del departamento (nombre en la banda azul)
        "department": department,  # en el template: {{ department.name }}

        # Semestre actual (badge a la derecha)
        "current_semester": "Enero - Junio 2025",

        # Notificaciones (campana arriba a la derecha)
        "notifications": notifications,
        "notifications_count": len(notifications),

        # Coordinador actual (tarjeta de “Designación de Coordinador”)
        "current_coordinator_name": "Dra. Elena Martínez",

        # Estado del PAT (tarjeta de planeación PAT)
        "pat_status": "En revisión",

        # Stats que se muestran en las tarjetas numéricas
        "dept_stats": dept_stats,
    }

    return render(request, "coordac/coordac_dashboard.html", context)
