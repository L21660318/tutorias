# apps/users/views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Usuarios fijos de prueba
        fixed_users = {
            'tutor': 'TUTOR',
            'subac': 'SUBAC',
            'jefe': 'JEFEDEPTO',
            'coordinst': 'COORDINST',
            'coordac': 'COORDAC',
            'tutee': 'TUTEE',
            'psych': 'PSYCHOLOGIST',
            'admin': 'SUPERUSER',
        }

        if username in fixed_users:
            # Crear usuario temporal en memoria (no requiere DB)
            user = User(username=username)
            role = fixed_users[username]
            user.role = role
            user.is_superuser = role == 'SUPERUSER'
            user.is_staff = user.is_superuser
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Loguear usuario
            login(request, user)
            return redirect(self.get_success_url())

        # Si no es usuario fijo, usar login normal
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
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
        else:
            return '/'

@login_required
def profile_view(request):
    user = request.user
    if not user.pk:
        # Usuario en memoria, no editable
        return render(request, 'users/profile.html', {'message': 'Usuario temporal, perfil no editable.'})

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'users/profile.html', {'form': form})

