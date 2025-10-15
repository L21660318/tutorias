from django.contrib import admin
from django.urls import path, include
from apps.tutoring.views import dashboard_view
from apps.academic.views import academic_view
from apps.users.views import CustomLoginView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views  # ✅ agregado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('tutoring/', dashboard_view, name='tutoring'),
    path('academic/', academic_view, name='academic'),
    path('jefe_depto/', include('apps.jefe_depto.urls')),
    path('coordinst/', include('apps.coordinst.urls')),
    path('coordac/', include('apps.coordac.urls')),
    path('tutee/', include('apps.tutee.urls')),
    path('jefe_deptodes/', include('apps.jefe_deptodes.urls')),
    path('psychologist/', include('apps.psychologist.urls')),
    path('profile/', user_views.profile_view, name='profile'),  # ✅ corregido
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
