# pit_sistema/urls.py

from django.contrib import admin
from django.urls import path
from apps.tutoring.views import dashboard_view  # <-- 1. IMPORTA LA VISTA

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'), # <-- 2. AÑADE ESTA LÍNEA
]