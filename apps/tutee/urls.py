from django.urls import path
from .views import tutee_view

urlpatterns = [
    path('', tutee_view, name='tutee_dashboard'),
]
