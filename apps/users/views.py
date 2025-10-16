# apps/users/views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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

# Sesión simulada (solo para prototipo)
TEMP_SESSION_KEY = 'temp_user'

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username in FIXED_USERS:
            # Guardar usuario temporal en "sesión" de prototipo
            request.session[TEMP_SESSION_KEY] = {
                'username': username,
                'role': FIXED_USERS[username],
                'is_superuser': FIXED_USERS[username] == 'SUPERUSER'
            }
            return redirect(self.get_success_url(request))

        return HttpResponse("Usuario o contraseña incorrecta.")

    def get_success_url(self, request):
        temp_user = request.session.get(TEMP_SESSION_KEY)
        if not temp_user:
            return '/'

        role = temp_user['role']
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
        elif temp_user['is_superuser']:
            return '/admin/'
        else:
            return '/'

def profile_view(request):
    temp_user = request.session.get(TEMP_SESSION_KEY)
    if temp_user:
        # Usuario temporal, no editable
        return render(request, 'users/profile.html', {
            'message': f"Usuario temporal: {temp_user['username']}. Perfil no editable."
        })

    # Aquí podrías agregar login real con base de datos si quieres
    return HttpResponse("Usuario no logueado.")
