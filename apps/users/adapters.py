# apps/users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError

class TecnmAccountAdapter(DefaultAccountAdapter):

    # (opcional) Validar correo si lo usas en registros locales
    def clean_email(self, email):
        email = super().clean_email(email)
        allowed_domains = ("@matehuala.tecnm.mx", "@tecnm.mx")
        if not email.endswith(allowed_domains):
            raise ValidationError(
                "Solo se permiten correos institucionales @matehuala.tecnm.mx o @tecnm.mx."
            )
        return email

    # 👇 ESTA ES LA CLAVE: redirección después de login (cualquier tipo)
    def get_login_redirect_url(self, request):
        user = request.user

        if not user.is_authenticated:
            return "/"

        # Redirección por rol, igual que en tu CustomLoginView
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
            return '/'
