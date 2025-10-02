# apps/users/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'TUTOR':
            return '/tutoring/'
        elif user.role == 'SUBAC':
            return '/academic/'
        elif user.role == 'JEFEDEPTO':
            return '/jefe_depto/'  # Asegúrate de crear esta vista y URL
        elif user.role == 'COORDINST':
            return '/coordinst/'  # Asegúrate de crear esta vista y URL
        elif user.role == 'COORDAC':
            return '/coordac/'  # Asegúrate de crear esta vista y URL
        elif user.role == 'TUTEE':
            return '/tutee/'  # Asegúrate de crear esta vista y URL
        elif user.role == 'JEFEDEPTODES':
            return '/jefe_deptodes/'  # Asegúrate de crear esta vista y URL
        elif user.is_superuser:
            return '/admin/'
        else:
            return '/'  # fallback
