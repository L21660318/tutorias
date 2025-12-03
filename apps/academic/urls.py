# apps/academic/urls.py

from django.urls import path
from .views import academic_view, plan_tutor_sessions_view

urlpatterns = [
    path('', academic_view, name='academic'),

]
