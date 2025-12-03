from django.urls import path
from .views import dashboard_view, assign_student_psychologist, schedule_session

urlpatterns = [
    path('', dashboard_view, name='psychologist_dashboard'),
    path('assign/', assign_student_psychologist, name='psychology_assign_student'),
    path(
        "psychologist/sessions/<int:pk>/schedule/",
        schedule_session,
        name="psychologist_schedule_session",
    ),
    
]
