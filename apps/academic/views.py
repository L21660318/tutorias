# apps/academic/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from django.contrib.auth import get_user_model
from .models import Period, AcademicDepartment, DepartmentCoordinator
from apps.tutoring.models import TutorGroup  # si ya lo usas arriba para otras vistas

User = get_user_model()

from apps.academic.models import Period
from apps.tutoring.models import TutorGroup
from apps.tutoring.services import generate_plan_sessions_for_group
from datetime import datetime


@login_required
def academic_view(request):
    return render(request, 'academic/dashboard.html')


@login_required
def plan_tutor_sessions_view(request):
    periods = Period.objects.all().order_by('-id')
    groups = TutorGroup.objects.select_related("tutor", "period").all()

    if request.method == "POST":
        period_id = request.POST.get("period")
        group_id = request.POST.get("group")   # 👈 AHORA LEEMOS "group", no "tutor"

        # 1) Validar período
        try:
            period = periods.get(pk=period_id)
        except Period.DoesNotExist:
            messages.error(request, "Período inválido.")
            return redirect(request.path)

        # 2) Decidir a qué grupos aplicar
        if group_id == "ALL":
            # Todos los grupos de ese período
            groups_to_apply = groups.filter(period=period)
        else:
            try:
                grp = groups.get(pk=group_id, period=period)
            except TutorGroup.DoesNotExist:
                messages.error(request, "Grupo inválido para ese período.")
                return redirect(request.path)
            groups_to_apply = [grp]

        # 3) Construir lista de 12 actividades
        activities = []
        for i in range(1, 13):
            title = request.POST.get(f"activity_title_{i}", "").strip()
            desc = request.POST.get(f"activity_desc_{i}", "").strip()
            date_str = request.POST.get(f"activity_date_{i}", "")
            file = request.FILES.get(f"activity_file_{i}")

            if not title:
                messages.error(request, f"La actividad {i} debe tener un título.")
                return redirect(request.path)

            date = None
            if date_str:
                # input type=datetime-local -> %Y-%m-%dT%H:%M
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

            activities.append({
                "number": i,
                "title": title,
                "description": desc,
                "date": date,
                "file": file,
            })

        # 4) Generar / actualizar sesiones para cada grupo
        for g in groups_to_apply:
            generate_plan_sessions_for_group(g, activities)

        messages.success(
            request,
            "Se han generado/actualizado las 12 sesiones del programa "
            "para los grupos seleccionados."
        )
        return redirect('academic_plan_sessions')

    return render(request, 'academic/plan_tutor_sessions.html', {
        "periods": periods,
        "groups": groups,
    })


@login_required
def academic_assign_coordinator(request):
    user = request.user

    # 🔐 Permisos: ajusta los roles que sí pueden entrar
    if getattr(user, "role", None) not in ["SUBAC", "ACADEMIC"] and not user.is_superuser:
        messages.error(request, "No tienes permisos para designar coordinadores de tutorías.")
        return redirect("academic")

    departments = AcademicDepartment.objects.filter(is_active=True).order_by("name")
    coordinators = User.objects.filter(role="COORDAC", is_active=True).order_by("first_name", "last_name")

    if request.method == "POST":
        dept_id = request.POST.get("department")

        if not dept_id:
            messages.error(request, "Debes seleccionar un departamento.")
            return redirect("academic_assign_coordinator")

        try:
            dept = departments.get(pk=dept_id)
        except AcademicDepartment.DoesNotExist:
            messages.error(request, "Departamento inválido.")
            return redirect("academic_assign_coordinator")

        # 🔹 Si viene capturado new_username, creamos usuario nuevo
        new_username = request.POST.get("new_username", "").strip()

        if new_username:
            # === CREAR NUEVO USUARIO COORDAC ===
            new_first_name = request.POST.get("new_first_name", "").strip()
            new_last_name = request.POST.get("new_last_name", "").strip()
            new_email = request.POST.get("new_email", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            new_password_confirm = request.POST.get("new_password_confirm", "").strip()

            # Validaciones básicas
            if not new_first_name or not new_last_name:
                messages.error(request, "Nombre y apellidos del coordinador son obligatorios.")
                return redirect("academic_assign_coordinator")

            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Ya existe un usuario con ese nombre de usuario.")
                return redirect("academic_assign_coordinator")

            if new_password and new_password != new_password_confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("academic_assign_coordinator")

            # Crear usuario
            coordinator = User(
                username=new_username,
                email=new_email,
                first_name=new_first_name,
                last_name=new_last_name,
                role="COORDAC",
                is_active=True,
            )
            if new_password:
                coordinator.set_password(new_password)
            else:
                # Si no pones contraseña, se crea sin contraseña utilizable
                coordinator.set_unusable_password()
            coordinator.save()

        else:
            # === USAR COORDINADOR EXISTENTE ===
            coord_id = request.POST.get("coordinator")
            if not coord_id:
                messages.error(
                    request,
                    "Selecciona un coordinador existente o captura los datos de uno nuevo."
                )
                return redirect("academic_assign_coordinator")

            try:
                coordinator = coordinators.get(pk=coord_id)
            except User.DoesNotExist:
                messages.error(request, "Coordinador inválido.")
                return redirect("academic_assign_coordinator")

        # 🔄 Desactivar coordinadores anteriores del departamento
        DepartmentCoordinator.objects.filter(
            department=dept,
            is_active=True
        ).update(
            is_active=False,
            end_date=timezone.now().date()
        )

        # ✅ Crear registro como nuevo coordinador activo
        DepartmentCoordinator.objects.create(
            department=dept,
            coordinator=coordinator,
            start_date=timezone.now().date(),
            is_active=True,
        )

        messages.success(
            request,
            f"{coordinator.get_full_name()} ha sido designado(a) coordinador(a) "
            f"del departamento {dept.name}."
        )
        return redirect("academic_assign_coordinator")

    return render(request, "academic/assign_coordinator.html", {
        "departments": departments,
        "coordinators": coordinators,
    })