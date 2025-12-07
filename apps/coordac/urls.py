from django.urls import path
from .views import coordac_tutor_compliance_view, coordac_view, coordac_tutor_compliance_pdf

urlpatterns = [
    path('', coordac_view, name='coordac_dashboard'),
    path(
        "tutors/compliance/",
        coordac_tutor_compliance_view,
        name="coordac_tutor_compliance",
    ),
    path(
        "tutors/compliance/pdf/",
        coordac_tutor_compliance_pdf,
        name="coordac_tutor_compliance_pdf",
    ),
]
