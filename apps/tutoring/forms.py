# apps/tutoring/forms.py

from django import forms
from django.contrib.auth import get_user_model

from .models import Session, TuteeProfile
from .models import TutorCoordinatorAssignment
from .models import TutoringReport
from .models import TutoringInterview

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
        fields = ['period', 'title', 'content', 'attachment']
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
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls'
            }),
        }
        labels = {
            'period': 'Periodo',
            'title': 'Título del reporte',
            'content': 'Contenido del reporte',
            'attachment': 'Archivo Excel del reporte',
        }


User = get_user_model()


class TutoringInterviewForm(forms.ModelForm):
    class Meta:
        model = TutoringInterview
        fields = ['tutee', 'scheduled_date', 'topic', 'summary']

    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

        # Solo mostrar a los alumnos que pertenecen a los grupos de ESTE tutor
        if tutor is not None:
            self.fields['tutee'].queryset = User.objects.filter(
                tutee_profile__group__tutor=tutor
            ).distinct().order_by('last_name', 'first_name')

        self.fields['tutee'].label = "Alumno entrevistado"
        self.fields['scheduled_date'].label = "Fecha y hora de la entrevista"
        self.fields['topic'].label = "Tema / motivo"
        self.fields['summary'].label = "Informe / resumen de la entrevista"

        # Estilos Bootstrap
        for name, field in self.fields.items():
            if name == 'scheduled_date':
                field.widget = forms.DateTimeInput(
                    attrs={'type': 'datetime-local', 'class': 'form-control'}
                )
            elif name == 'summary':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': "Anota aquí los puntos principales tratados, acuerdos, observaciones, etc."
                })
            else:
                field.widget.attrs.update({'class': 'form-control'})
