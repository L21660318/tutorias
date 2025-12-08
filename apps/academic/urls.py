# apps/academic/urls.py

from django.urls import path
from .views import academic_view, plan_tutor_sessions_view, subac_group_certificates_list, subac_validate_group_certificate

urlpatterns = [
    path('', academic_view, name='academic'),
    path(
        "group-certificates/",
        subac_group_certificates_list,
        name="subac_group_certificates"
    ),
    path(
        "group-certificates/<int:pk>/validate/",
        subac_validate_group_certificate,
        name="subac_validate_group_certificate"
    ),

]
