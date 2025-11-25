from django.urls import path
from .views import tutee_dashboard

urlpatterns = [
    path('', tutee_dashboard, name='tutee_dashboard'),
]
