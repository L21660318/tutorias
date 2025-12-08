from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

User = get_user_model()

ALLOWED_DOMAINS = ("matehuala.tecnm.mx", "tecnm.mx")


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Validar que llenó ambos campos
        if not identifier or not password:
            messages.error(request, "Debes ingresar usuario/correo y contraseña.")
            return render(request, self.template_name)

        # ----- CASO 1: LOGIN POR CORREO -----
        if '@' in identifier:
            local, _, domain = identifier.partition('@')

            # Validar dominio
            if domain.lower() not in ALLOWED_DOMAINS:
                messages.error(
                    request,
                    "Solo se permiten correos @matehuala.tecnm.mx o @tecnm.mx."
                )
                return render(request, self.template_name)

            # Buscar usuario por correo institucional
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                messages.error(request, "Usuario o contraseña incorrectos.")
                return render(request, self.template_name)

        # ----- CASO 2: LOGIN POR USERNAME -----
        else:
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                messages.error(request, "Usuario o contraseña incorrectos.")
                return render(request, self.template_name)

        # Autenticar con el username real del usuario
        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, self.template_name)

        # Login OK
        login(request, user_auth)
        return redirect(self.get_success_url())

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
            return '/'


@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'users/profile.html', {'form': form})



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def post_login_redirect(request):
    user = request.user

    # Si el usuario viene de Microsoft y no tiene rol aún,
    # y su correo es @matehuala.tecnm.mx => lo marcamos como TUTEE
    email = (user.email or "").lower()
    if not user.role and email.endswith("@matehuala.tecnm.mx"):
        user.role = "TUTEE"
        user.save(update_fields=["role"])

    # Redirección por rol (igual que en tu CustomLoginView)
    if user.role == 'TUTOR':
        return redirect('/tutoring/')
    elif user.role == 'SUBAC':
        return redirect('/academic/')
    elif user.role == 'JEFEDEPTO':
        return redirect('/jefe_depto/')
    elif user.role == 'COORDINST':
        return redirect('/coordinst/')
    elif user.role == 'COORDAC':
        return redirect('/coordac/')
    elif user.role == 'TUTEE':
        return redirect('/tutee/')
    elif user.role == 'JEFEDEPTODES':
        return redirect('/jefe_deptodes/')
    elif user.role == 'PSYCHOLOGIST':
        return redirect('/psychologist/')
    elif user.is_superuser:
        return redirect('/admin/')
    else:
        # Si no tiene rol, mándalo al login otra vez
        return redirect('/')
