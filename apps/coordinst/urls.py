from django.urls import path
from .views import coordinst_dashboard

urlpatterns = [
    path('', coordinst_dashboard, name='coordinst_dashboard'),
]
