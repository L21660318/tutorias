# apps/tutoring/views.py

from django.shortcuts import render

def dashboard_view(request):
    """
    Esta vista renderiza la página principal o dashboard.
    """
    # En el futuro, aquí puedes pasar datos a la plantilla.
    # Por ejemplo: proximas_sesiones = Session.objects.filter(...)
    context = {} 
    
    return render(request, 'tutoring/dashboard.html', context)