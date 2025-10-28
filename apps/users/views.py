<<<<<<< HEAD
=======
# apps/users/views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
>>>>>>> 10b92fa73976cb5ff74c1715a4c44a699be0955f
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
<<<<<<< HEAD
from django.contrib import messages
from django.db.models import Q
from .forms import ProfileForm

User = get_user_model()  # ✅ obtiene tu modelo personalizado 'users.User'

=======
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
>>>>>>> 10b92fa73976cb5ff74c1715a4c44a699be0955f

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

<<<<<<< HEAD
    def post(self, request, *args, **kwargs):
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Buscar usuario por nombre de usuario o correo
        try:
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
        except User.DoesNotExist:
            messages.error(request, "Usuario o correo no encontrado.")
            return render(request, self.template_name)

        # Autenticar con el nombre de usuario real
        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Contraseña incorrecta.")
            return render(request, self.template_name)

    def get_success_url(self):
        user = self.request.user
=======
    def get(self, request):
        return render(request, self.template_name)
>>>>>>> 10b92fa73976cb5ff74c1715a4c44a699be0955f

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
