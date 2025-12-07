from django.urls import path
from .views import coordinst_dashboard, coordinst_report_list

urlpatterns = [
    path('', coordinst_dashboard, name='coordinst_dashboard'),
    path("reports/", coordinst_report_list, name="coordinst_report_list"),
]
