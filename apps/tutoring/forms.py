# apps/tutoring/forms.py

from django import forms
from django.contrib.auth import get_user_model

from .models import Session, TuteeProfile

User = get_user_model()


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["tutee", "period", "scheduled_date", "status", "session_summary", "agreements"]
        widgets = {
            "tutee": forms.Select(attrs={"class": "form-select"}),
            "period": forms.Select(attrs={"class": "form-select"}),
            "scheduled_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "session_summary": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "agreements": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop("tutor", None)
        super().__init__(*args, **kwargs)

        # Solo mostrar tutorados asignados a este tutor
        if tutor is not None:
            self.fields["tutee"].queryset = User.objects.filter(
                tutee_profile__assigned_tutor=tutor
            )
