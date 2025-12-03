from django.contrib import admin
from django.urls import path, include
from apps.tutoring.views import dashboard_view, create_session, tutoring_session_detail, tutor_report_create, tutor_report_list, coordinator_report_inbox
from apps.academic.views import academic_view, plan_tutor_sessions_view, academic_assign_coordinator
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
    #------------------------------------------

    #---------------Academic URLs --------------
    path('academic/', academic_view, name='academic'),
    path('plan-sessions/', plan_tutor_sessions_view, name='academic_plan_sessions'),
    path('academic/department-coordinator/', academic_assign_coordinator, name='academic_assign_coordinator'),
    #----------------------------------------------
    #------------------ User URLs ----------------
    path('jefe_depto/', include('apps.jefe_depto.urls')),
    path('jefe_depto/assign-coordinator/', jefe_views.assign_coordinator, name='jefe_depto_assign_coordinator'),
    #------------------ Coordinator URLs ----------------
    path('coordinst/', include('apps.coordinst.urls')),
    path('coordac/', include('apps.coordac.urls')),
    path('tutee/', include('apps.tutee.urls')),
    path('jefe_deptodes/', include('apps.jefe_deptodes.urls')),
    #------------------ Psicólogo URLs ----------------
    path('psychologist/', include('apps.psychologist.urls')),
    #----------------------------------------
    path('profile/', user_views.profile_view, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
