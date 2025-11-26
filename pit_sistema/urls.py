from django.contrib import admin
from django.urls import path, include
from apps.tutoring.views import dashboard_view, create_session
from apps.academic.views import academic_view
# from apps.users.views import CustomLoginView   # 👈 ya no lo usamos por ahora
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views
from apps.users.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👇 CAMBIAR ESTA LÍNEA
    path('', CustomLoginView.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),
    #------------- Tutoring URLs --------------
    path('tutoring/', dashboard_view, name='tutoring'),
    path('tutoring/sessions/new/', create_session, name='tutoring_session_new'),
    #------------------------------------------

    path('academic/', academic_view, name='academic'),
    path('jefe_depto/', include('apps.jefe_depto.urls')),
    path('coordinst/', include('apps.coordinst.urls')),
    path('coordac/', include('apps.coordac.urls')),
    path('tutee/', include('apps.tutee.urls')),
    path('jefe_deptodes/', include('apps.jefe_deptodes.urls')),
    path('psychologist/', include('apps.psychologist.urls')),
    path('profile/', user_views.profile_view, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
