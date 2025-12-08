
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.tutoring.models import TutorGroupCertificate, TutoringReport

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

    certificates = (
        TutorGroupCertificate.objects
        .filter(coordinator=request.user)
        .select_related("tutor", "group", "period")
        .order_by("-uploaded_at")
    )


    context = {
        "stats": stats,
        "compliance_reports": compliance_reports,  # 👈 PASARLOS AL TEMPLATE
        "group_certificates": certificates,
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

# apps/coordinst/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.tutoring.forms import TutorGroupCertificateForm
from apps.tutoring.models import TutorGroupCertificate

# apps/coordinst/views.py
@login_required
def upload_group_certificate(request):
    if request.user.role != "COORDINST":
        return redirect("/")  # o 403

    if request.method == "POST":
        form = TutorGroupCertificateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.coordinator = request.user
            cert.tutor = form.cleaned_data["group"].tutor
            cert.period = form.cleaned_data["group"].period
            cert.save()
            return redirect("coordinst:dashboard")  # 👈 AQUÍ EL CAMBIO
    else:
        form = TutorGroupCertificateForm(user=request.user)

    return render(request, "coordinst/upload_group_certificate.html", {"form": form})
