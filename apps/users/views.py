from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .forms import ProfileForm

User = get_user_model()  # ✅ obtiene tu modelo personalizado 'users.User'


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

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

        if user.role == 'TUTOR':
            return '/tutoring/'
        elif user.role == 'SUBAC':
            return '/academic/'
        elif user.role == 'JEFEDEPTO':
            return '/jefe_depto/'
        elif user.role == 'COORDINST':
            return '/coordinst/'
        elif user.role == 'COORDAC':
            return '/coordac/'
        elif user.role == 'TUTEE':
            return '/tutee/'
        elif user.role == 'JEFEDEPTODES':
            return '/jefe_deptodes/'
        elif user.role == 'PSYCHOLOGIST':
            return '/psychologist/'
        elif user.is_superuser:
            return '/admin/'
        else:
            return '/'  # fallback


@login_required
def profile_view(request):
    """Vista para que el usuario edite su perfil (nombre, email, foto, etc.)."""
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'users/profile.html', {'form': form})
