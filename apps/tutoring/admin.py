from django.contrib import admin
from .models import TuteeProfile, Session, Alert, InterventionGuide

admin.site.register(TuteeProfile)
admin.site.register(Session)
admin.site.register(Alert)
admin.site.register(InterventionGuide)