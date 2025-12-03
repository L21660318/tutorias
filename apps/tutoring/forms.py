# apps/tutoring/forms.py

from django import forms
from django.contrib.auth import get_user_model

from .models import Session, TuteeProfile
from .models import TutorCoordinatorAssignment
from .models import TutoringReport
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

class AssignTutorCoordinatorForm(forms.ModelForm):
    class Meta:
        model = TutorCoordinatorAssignment
        fields = ['tutor', 'coordinator']

    def __init__(self, *args, **kwargs):
        jefe_depto = kwargs.pop('jefe_depto', None)  # por si luego quieres filtrar por departamento
        super().__init__(*args, **kwargs)

        # Filtramos por rol
        self.fields['tutor'].queryset = User.objects.filter(role='TUTOR').order_by('first_name', 'last_name')
        self.fields['coordinator'].queryset = User.objects.filter(role='COORDINADOR').order_by('first_name', 'last_name')

        self.fields['tutor'].label = "Tutor"
        self.fields['coordinator'].label = "Coordinador(a)"


class TutoringReportForm(forms.ModelForm):
    class Meta:
        model = TutoringReport
        # Tutor y coordinator los llenamos en la vista; aquí solo lo que el tutor escribe
        fields = ['period', 'title', 'content']
        widgets = {
            'period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Enero - Junio 2025'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Informe semestral de acción tutorial'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describa las actividades, avances, problemáticas y resultados de la acción tutorial...'
            }),
        }
        labels = {
            'period': 'Periodo',
            'title': 'Título del reporte',
            'content': 'Contenido del reporte',
        }