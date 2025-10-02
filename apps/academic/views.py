from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def academic_view(request):
    return render(request, 'academic/dashboard.html')  # crea este template
