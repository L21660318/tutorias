from django.urls import path
from .views import coordac_view

urlpatterns = [
    path('', coordac_view, name='coordac_dashboard'),
]
