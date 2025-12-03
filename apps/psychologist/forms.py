from django import forms
from .models import PsychologySession
from apps.users.models import User


class PsychologySessionAssignForm(forms.ModelForm):
    class Meta:
        model = PsychologySession
        # 🔹 El tutor SOLO canaliza: nada de fecha/hora
        fields = [
            "student",
            "psychologist",
            "reason",
            "risk_level",
            "performance_level",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Solo usuarios con rol PSYCHOLOGIST
        self.fields["psychologist"].queryset = User.objects.filter(
            role="PSYCHOLOGIST", is_active=True
        )

        # Opcional: un poquito de estilo bootstrap
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")

class PsychologySessionScheduleForm(forms.ModelForm):
    class Meta:
        model = PsychologySession
        fields = ["session_date", "session_time"]
        widgets = {
            "session_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "session_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
        }
        labels = {
            "session_date": "Fecha de la sesión",
            "session_time": "Hora de la sesión",
        }