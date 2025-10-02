from django.shortcuts import render

def coordac_view(request):
    return render(request, 'coordac/coordac_dashboard.html')
