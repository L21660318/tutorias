from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 🔹 IMPORTA MODELOS RELACIONADOS
from apps.tutoring.models import TuteeProfile, Session, Alert
from apps.academic.models import Career, Period  # ajusta si tu Period se llama diferente


class TuteeProfileInline(admin.StackedInline):
    model = TuteeProfile
    fk_name = "user"
    extra = 0


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password', 'role')
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'role',
                'is_staff',
                'is_active'
            ),
        }),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # 🔹 Inline para poder ver/editar la ficha de tutorado
    inlines = [TuteeProfileInline]

    # 🔹 (Opcional) Solo mostrar el inline cuando el usuario es TUTEE
    def get_inlines(self, request, obj=None):
        if obj is not None and obj.role == "TUTEE":
            return [TuteeProfileInline]
        return []


admin.site.register(User, CustomUserAdmin)
