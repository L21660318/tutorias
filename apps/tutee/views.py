from django.shortcuts import render

def tutee_view(request):
    return render(request, 'tutee/tutee_dashboard.html')
