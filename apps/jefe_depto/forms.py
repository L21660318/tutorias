# apps/jefe_depto/forms.py
from django import forms
from apps.users.models import User
from apps.tutoring.models import TutorCoordinatorAssignment  # 👈 IMPORT CORRECTO

class AssignTutorCoordinatorForm(forms.ModelForm):
    class Meta:
        model = TutorCoordinatorAssignment
        fields = ['tutor', 'coordinator']

    def __init__(self, *args, **kwargs):
        jefe_depto = kwargs.pop('jefe_depto', None)
        super().__init__(*args, **kwargs)

        # 🔹 Tutores (rol TUTOR)
        self.fields['tutor'].queryset = User.objects.filter(
            role='TUTOR'
        ).order_by('first_name', 'last_name')

        # 🔹 Coordinadores académicos (rol COORDAC)
        self.fields['coordinator'].queryset = User.objects.filter(
            role='COORDAC'
        ).order_by('first_name', 'last_name')

        # Labels
        self.fields['tutor'].label = "Tutor"
        self.fields['coordinator'].label = "Coordinador(a) de tutorías"

        # Estilos Bootstrap
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-select'})
