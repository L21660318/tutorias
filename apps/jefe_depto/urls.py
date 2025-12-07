from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='jefe_depto_dashboard'),
    path(
        'jefe_depto/asignar-tutor-coordinador/',
        views.assign_tutor_to_coordinator,
        name='assign_tutor_to_coordinator'
    ),
    path("", views.jefe_depto_view, name="jefe_depto_dashboard"),
]
