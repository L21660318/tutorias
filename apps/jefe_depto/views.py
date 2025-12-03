# apps/jefe_depto/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.academic.models import AcademicDepartment, DepartmentCoordinator

from .forms import AssignTutorCoordinatorForm
from apps.tutoring.models import TutorCoordinatorAssignment

User = get_user_model()

def is_jefe_depto(user):
    return getattr(user, 'role', None) == 'JEFEDEPTO'

@login_required
def dashboard(request):
    return render(request, 'jefe_depto/dashboard.html')


@login_required
def assign_coordinator(request):
    user = request.user

    # Solo Jefe de Departamento (y opcional JEFEDEPTODES) o superuser
    if getattr(user, "role", None) not in ["JEFEDEPTO", "JEFEDEPTODES"] and not user.is_superuser:
        messages.error(request, "No tienes permisos para designar coordinadores de tutorías.")
        return redirect('jefe_depto_dashboard')

    departments = AcademicDepartment.objects.filter(is_active=True).order_by("name")
    coordinators = User.objects.filter(role="COORDAC", is_active=True).order_by("first_name", "last_name")

    if request.method == "POST":
        dept_id = request.POST.get("department")

        if not dept_id:
            messages.error(request, "Debes seleccionar un departamento.")
            return redirect("jefe_depto_assign_coordinator")

        try:
            dept = departments.get(pk=dept_id)
        except AcademicDepartment.DoesNotExist:
            messages.error(request, "Departamento inválido.")
            return redirect("jefe_depto_assign_coordinator")

        # Si viene new_username, creamos usuario COORDAC nuevo
        new_username = request.POST.get("new_username", "").strip()

        if new_username:
            new_first_name = request.POST.get("new_first_name", "").strip()
            new_last_name = request.POST.get("new_last_name", "").strip()
            new_email = request.POST.get("new_email", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            new_password_confirm = request.POST.get("new_password_confirm", "").strip()

            if not new_first_name or not new_last_name:
                messages.error(request, "Nombre y apellidos del coordinador son obligatorios.")
                return redirect("jefe_depto_assign_coordinator")

            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Ya existe un usuario con ese nombre de usuario.")
                return redirect("jefe_depto_assign_coordinator")

            if new_password and new_password != new_password_confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("jefe_depto_assign_coordinator")

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
                coordinator.set_unusable_password()
            coordinator.save()

        else:
            # Usar coordinador existente
            coord_id = request.POST.get("coordinator")
            if not coord_id:
                messages.error(
                    request,
                    "Selecciona un coordinador existente o captura los datos de uno nuevo."
                )
                return redirect("jefe_depto_assign_coordinator")

            try:
                coordinator = coordinators.get(pk=coord_id)
            except User.DoesNotExist:
                messages.error(request, "Coordinador inválido.")
                return redirect("jefe_depto_assign_coordinator")

        # Desactivar coordinador(es) anterior(es) del departamento
        DepartmentCoordinator.objects.filter(
            department=dept,
            is_active=True
        ).update(
            is_active=False,
            end_date=timezone.now().date()
        )

        # Crear el nuevo coordinador activo
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
        return redirect("jefe_depto_assign_coordinator")

    return render(request, "academic/assign_coordinator.html", {
        "departments": departments,
        "coordinators": coordinators,
    })

@login_required
def assign_tutor_to_coordinator(request):
    if not is_jefe_depto(request.user):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('home')  # o la vista que uses

    if request.method == 'POST':
        form = AssignTutorCoordinatorForm(request.POST, jefe_depto=request.user)
        if form.is_valid():
            # 👇 opción simple: crear/actualizar por tutor
            tutor = form.cleaned_data['tutor']
            coordinator = form.cleaned_data['coordinator']

            assignment, created = TutorCoordinatorAssignment.objects.update_or_create(
                tutor=tutor,
                defaults={'coordinator': coordinator}
            )

            if created:
                messages.success(
                    request,
                    f"Se asignó el tutor {assignment.tutor} al coordinador {assignment.coordinator}."
                )
            else:
                messages.success(
                    request,
                    f"Se actualizó la asignación del tutor {assignment.tutor} al coordinador {assignment.coordinator}."
                )
            return redirect('assign_tutor_to_coordinator')
        else:
            # 👇 para ver por qué no guarda (si el form es inválido)
            messages.error(request, f"Formulario inválido: {form.errors.as_text()}")
    else:
        form = AssignTutorCoordinatorForm(jefe_depto=request.user)

    assignments = TutorCoordinatorAssignment.objects.select_related('tutor', 'coordinator').all()

    context = {
        'form': form,
        'assignments': assignments,
    }
    return render(request, 'jefe_depto/assign_tutor_to_coordinator.html', context)