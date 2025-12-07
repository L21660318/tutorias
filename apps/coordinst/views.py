
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.tutoring.models import TutoringReport

from apps.tutoring.models import TutorComplianceReport  

def is_coordinst(user):
    return getattr(user, "role", None) == "COORDINST"


@login_required
def coordinst_dashboard(request):
    # 👉 Valida rol (o déjalo sin validación si aún no usas role)
    if not is_coordinst(request.user) and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a este panel.")
        return redirect("home")

    # Aquí van las stats dummy que ya usas (si tienes context previo, mantenlo)
    stats = {}

    # 🔹 NUEVO: traer TODOS los reportes de cumplimiento
    compliance_reports = (
        TutorComplianceReport.objects
        .select_related("coordinator", "period")
        .order_by("-generated_at")
    )


    context = {
        "stats": stats,
        "compliance_reports": compliance_reports,  # 👈 PASARLOS AL TEMPLATE
    }

    return render(request, 'coordinst/dashboard.html', context)



@login_required
def coordinst_report_list(request):
    # Solo coordinación institucional
    if not is_coordinst(request.user):
        messages.error(request, "Solo la Coordinación Institucional puede ver estos reportes.")
        return redirect("home")

    reports = (
        TutoringReport.objects
        .filter(status="SENT_TO_HEAD")  # 👈 mismos que ve el JEFEDEPTO
        .select_related("tutor", "coordinator")
        .order_by("-sent_to_head_at", "-created_at")
    )

    context = {
        "reports": reports,
    }
    return render(request, "coordinst/report_list.html", context)


