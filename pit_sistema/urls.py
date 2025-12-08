from django.contrib import admin
from django.urls import path, include
from apps.coordinst.views import coordinst_report_list
from apps.tutoring.views import dept_head_dashboard,dept_head_report_list,coordinator_report_detail, interview_create,interview_list ,dashboard_view, create_session, interview_update, tutor_certificates_view, tutor_report_update, tutoring_session_detail, tutor_report_create, tutor_report_list, coordinator_report_inbox
from apps.academic.views import academic_view, plan_tutor_sessions_view, academic_assign_coordinator, subac_group_certificates_list, subac_validate_group_certificate
# from apps.users.views import CustomLoginView   # 👈 ya no lo usamos por ahora
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views
from apps.users.views import CustomLoginView
from apps.jefe_depto import views as jefe_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👇 CAMBIAR ESTA LÍNEA
    path('', CustomLoginView.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),
    #------------- Tutoring URLs --------------
    path('tutoring/', dashboard_view, name='tutoring'),
    path('tutoring/sessions/new/', create_session, name='tutoring_session_new'),\
    path(
        "sessions/<int:pk>/",
        tutoring_session_detail,
        name="tutoring_session_detail"
    ),
    path('reports/generate/', tutor_report_create, name='tutor_report_create'),
    path('reports/my/', tutor_report_list, name='tutor_report_list'),
    path('coordac/reports/', coordinator_report_inbox, name='coordinator_report_inbox'),
    path('reports/<int:pk>/edit/', tutor_report_update, name='tutor_report_update'),
    path('interviews/', interview_list, name='interview_list'),
    path('interviews/new/', interview_create, name='interview_create'),
    path('interviews/<int:pk>/', interview_update, name='interview_update'),
    path('reports/inbox/', coordinator_report_inbox,name='coordinator_report_inbox'),
    path('reports/<int:pk>/', coordinator_report_detail, name='coordinator_report_detail'),
    path('dept-head/reports/', dept_head_report_list, name='dept_head_report_list'),
    path("certificates/", tutor_certificates_view, name="tutor_certificates"),
    
    #------------------------------------------

    #---------------Academic URLs --------------
    path('academic/', academic_view, name='academic'),
    path('plan-sessions/', plan_tutor_sessions_view, name='academic_plan_sessions'),
    path('academic/department-coordinator/', academic_assign_coordinator, name='academic_assign_coordinator'),
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
    #----------------------------------------------
   #------------------ Jefe de Depto URLs ----------------
    path('jefe_depto/', jefe_views.jefe_depto_view, name='jefe_depto_dashboard'),

    path('jefe_depto/', dept_head_dashboard, name='dept_head_dashboard'),

    path(
        'jefe_depto/assign-coordinator/',
        jefe_views.assign_coordinator,
        name='jefe_depto_assign_coordinator'
    ),

    path(
        'jefe_depto/assign-tutor-coordinator/',
        jefe_views.assign_tutor_to_coordinator,   # 👈 ESTA VISTA YA LA DEBES TENER EN apps.jefe_depto.views
        name='assign_tutor_to_coordinator'        # 👈 ESTE NAME ES EL QUE PIDE EL TEMPLATE
    ),

    #------------- CORDINACIÓN INSTITUCIONAL URLs --------------
    path('coordinst/', include('apps.coordinst.urls')),
    path("reports/", coordinst_report_list, name="coordinst_report_list"),
    #------------------ Coordinador de Área URLs ----------------
    path('coordac/', include('apps.coordac.urls')),
    path('tutee/', include('apps.tutee.urls')),
    path('jefe_deptodes/', include('apps.jefe_deptodes.urls')),
    #------------------ Psicólogo URLs ----------------
    path('psychologist/', include('apps.psychologist.urls')),
    #----------------------------------------
    path('profile/', user_views.profile_view, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
