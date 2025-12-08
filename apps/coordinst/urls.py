# apps/coordinst/urls.py
from django.urls import path
from .views import coordinst_dashboard, coordinst_report_list, upload_group_certificate

app_name = "coordinst"

urlpatterns = [
    path("", coordinst_dashboard, name="dashboard"),
    path("reports/", coordinst_report_list, name="report_list"),
    path("upload-certificate/", upload_group_certificate, name="upload_group_certificate"),
]
