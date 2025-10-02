from django.shortcuts import render

def dashboard(request):
    return render(request, 'jefe_depto/dashboard.html')
