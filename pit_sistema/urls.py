from django.contrib import admin
from django.urls import path, include
from apps.tutoring.views import dashboard_view
from apps.academic.views import academic_view
from apps.users.views import CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin clásico
    path('', CustomLoginView.as_view(), name='login'),  # Pantalla principal: login
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('tutoring/', dashboard_view, name='tutoring'),
    path('academic/', academic_view, name='academic'),
    path('jefe_depto/', include('apps.jefe_depto.urls')),  # <--- esta línea
    path('coordinst/', include('apps.coordinst.urls')),
    path('coordac/', include('apps.coordac.urls')),  # <-- esta línea
    path('tutee/', include('apps.tutee.urls')),
    path('jefe_deptodes/', include('apps.jefe_deptodes.urls')),
    path('psychologist/', include('apps.psychologist.urls')),

]
