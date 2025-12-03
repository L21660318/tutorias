from django.urls import path
from .views import tutee_activities_view, tutee_dashboard

urlpatterns = [
    path('', tutee_dashboard, name='tutee_dashboard'),
    path('activities/', tutee_activities_view, name='tutee_activities'),
]
