from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.tutoring.models import TutorCoordinatorAssignment, TutorCompliance
from apps.academic.models import Period
from django.contrib.auth import get_user_model

User = get_user_model()


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



def is_coordac(user):
    return getattr(user, "role", None) in ("COORDAC", "COORDINADOR")


from django.http import HttpResponse
from django.template.loader import render_to_string

def is_jefe_depto(user):
    return getattr(user, "role", None) == "JEFEDEPTO"


@login_required
def coordac_tutor_compliance_pdf(request):
    # Puede verlo COORDAC, JEFEDEPTO y COORDINST
    if not (is_coordac(request.user) or is_jefe_depto(request.user) or is_coordinst(request.user)):
        messages.error(request, "No tienes permisos para ver este reporte.")
        return redirect("home")

    period = Period.objects.filter(is_active=True).first()
    if not period:
        messages.error(request, "No hay un periodo activo configurado.")
        return redirect("home")

    # Si es COORDAC, solo ve sus tutores; si es JEFE/COORDINST, ve todos
    if is_coordac(request.user):
        compliances = TutorCompliance.objects.filter(
            coordinator=request.user,
            period=period,
        ).select_related("tutor", "coordinator")
    else:
        compliances = TutorCompliance.objects.filter(
            period=period,
        ).select_related("tutor", "coordinator")

    html = render_to_string("tutoring/tutor_compliance_pdf.html", {
        "period": period,
        "compliances": compliances,
    })

    # Por ahora lo regresamos como HTML normal
    # Aquí puedes integrar tu librería de PDF si ya tienes una
    response = HttpResponse(html)
    return response


@login_required
def coordac_tutor_compliance_view(request):
    if not is_coordac(request.user):
        messages.error(request, "Solo la coordinación de tutorías puede acceder aquí.")
        return redirect("home")

    # Periodo actual (ajusta según tu modelo Period)
    period = Period.objects.filter(is_active=True).first()
    if not period:
        messages.error(request, "No hay un periodo activo configurado.")
        return redirect("home")

    # Tutores asignados a este coordinador
    assignments = (
        TutorCoordinatorAssignment.objects
        .filter(coordinator=request.user)
        .select_related("tutor")
    )

    tutors = [a.tutor for a in assignments]

    # Registros existentes de cumplimiento en este periodo
    existing = {
        c.tutor_id: c
        for c in TutorCompliance.objects.filter(
            coordinator=request.user,
            period=period
        )
    }

    if request.method == "POST":
        for tutor in tutors:
            value = request.POST.get(f"status_{tutor.id}")  # "COMPLIED" / "NOT_COMPLIED"
            comments = request.POST.get(f"comments_{tutor.id}", "").strip()

            if not value:
                continue  # si no marcó nada, lo dejamos igual

            obj, created = TutorCompliance.objects.get_or_create(
                coordinator=request.user,
                tutor=tutor,
                period=period,
                defaults={"status": value, "comments": comments},
            )
            obj.status = value
            obj.comments = comments
            obj.save()

        messages.success(request, "Cumplimiento de tutores guardado correctamente.")
        return redirect("coordac_tutor_compliance")

    context = {
        "period": period,
        "assignments": assignments,
        "existing": existing,
    }
    return render(request, "coordac/tutor_compliance.html", context)



from io import BytesIO
from xhtml2pdf import pisa
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.tutoring.models import TutorCompliance, TutorComplianceReport
from apps.academic.models import Period


@login_required
def coordac_tutor_compliance_pdf(request):
    # Puede verlo COORDAC, JEFEDEPTO y COORDINST
    if not (is_coordac(request.user) or is_jefe_depto(request.user) or is_coordinst(request.user)):
        messages.error(request, "No tienes permisos para ver este reporte.")
        return redirect("home")

    period = Period.objects.filter(is_active=True).first()
    if not period:
        messages.error(request, "No hay un periodo activo configurado.")
        return redirect("home")

    # Si es COORDAC, solo ve sus tutores; si es JEFE/COORDINST, ve todos
    if is_coordac(request.user):
        compliances = TutorCompliance.objects.filter(
            coordinator=request.user,
            period=period,
        ).select_related("tutor", "coordinator")
        coordinator = request.user
    else:
        compliances = TutorCompliance.objects.filter(
            period=period,
        ).select_related("tutor", "coordinator")
        coordinator = request.user

    # 1) Render HTML del reporte
    html_string = render_to_string(
        "tutoring/tutor_compliance_pdf.html",
        {
            "period": period,
            "compliances": compliances,
            "coordinator": coordinator,
        }
    )

    # 2) Convertir HTML → PDF con xhtml2pdf
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        src=html_string,
        dest=pdf_buffer,
        encoding="UTF-8",
    )

    if pisa_status.err:
        messages.error(request, "Ocurrió un error al generar el PDF.")
        return redirect("coordac_tutor_compliance")

    pdf_bytes = pdf_buffer.getvalue()

    # 3) Guardar en BD y sistema de archivos
    filename = f"reporte_cumplimiento_{coordinator.id}_{period.id}.pdf"

    report, created = TutorComplianceReport.objects.get_or_create(
        coordinator=coordinator,
        period=period,
    )
    report.pdf.save(filename, ContentFile(pdf_bytes), save=True)

    # 4) Devolver el PDF al navegador
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
