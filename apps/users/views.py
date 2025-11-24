# apps/users/views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProfileForm

# Usuarios fijos de prueba
FIXED_USERS = {
    'tutor': 'TUTOR',
    'subac': 'SUBAC',
    'jefe': 'JEFEDEPTO',
    'coordinst': 'COORDINST',
    'coordac': 'COORDAC',
    'tutee': 'TUTEE',
    'psych': 'PSYCHOLOGIST',
    'admin': 'SUPERUSER',
}

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username in FIXED_USERS:
            role = FIXED_USERS[username]
            # Creamos un usuario en memoria (no guardamos en DB)
            user = User(username=username)
            user.is_staff = role == 'SUPERUSER'
            user.is_superuser = role == 'SUPERUSER'
            # Guardamos un atributo "role" extra
            user.role = role
            # Necesario para que Django login funcione sin DB
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Logueamos al usuario
            login(request, user)
            return redirect(self.get_success_url(user))

        return HttpResponse("Usuario o contraseña incorrecta.")

    def get_success_url(self, user):
        role = getattr(user, 'role', None)
        if role == 'TUTOR':
            return '/tutoring/'
        elif role == 'SUBAC':
            return '/academic/'
        elif role == 'JEFEDEPTO':
            return '/jefe_depto/'
        elif role == 'COORDINST':
            return '/coordinst/'
        elif role == 'COORDAC':
            return '/coordac/'
        elif role == 'TUTEE':
            return '/tutee/'
        elif role == 'JEFEDEPTODES':
            return '/jefe_deptodes/'
        elif role == 'PSYCHOLOGIST':
            return '/psychologist/'
        elif user.is_superuser:
            return '/admin/'
        return '/'

@login_required
def profile_view(request):
    user = request.user
    if not hasattr(user, 'pk') or user.pk is None:
        # Usuario temporal
        return render(request, 'users/profile.html', {
            'message': f"Usuario temporal: {user.username}. Perfil no editable."
        })

    # Usuario real (DB)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'users/profile.html', {'form': form})
