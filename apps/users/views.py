# apps/users/views.py

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

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
