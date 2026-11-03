from django import forms
from .models import Paciente
from apps.empresas.models import Empresa


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'apellido', 'nombres', 'dni', 'cuil',
            'direccion', 'tel_movil', 'email',
            'empresa', 'estado_civil', 'sexo',
            'nacionalidad', 'tarea_propuesta',
        ]
        widgets = {
            'apellido':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: García'}),
            'nombres':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Carlos'}),
            'dni':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI o Pasaporte'}),
            'cuil':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20123456789', 'maxlength': '11'}),
            'direccion':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
            'tel_movil':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +54 9 11 1234-5678'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'empresa':         forms.Select(attrs={'class': 'form-control'}),
            'estado_civil':    forms.Select(attrs={'class': 'form-control'}),
            'sexo':            forms.Select(attrs={'class': 'form-control'}),
            'nacionalidad':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Argentina'}),
            'tarea_propuesta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción de la tarea propuesta...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo empresas activas en el desplegable
        self.fields['empresa'].queryset = Empresa.objects.filter(activa=True).order_by('nombre')
        self.fields['empresa'].empty_label = '— Sin empresa —'
        # Agregar opción vacía a los selects de choices
        self.fields['estado_civil'].empty_value = ''
        self.fields['sexo'].empty_value = ''

    def clean_cuil(self):
        cuil = self.cleaned_data.get('cuil', '').strip()
        if cuil and not cuil.isdigit():
            raise forms.ValidationError('El CUIL debe contener solo dígitos numéricos.')
        if cuil and len(cuil) != 11:
            raise forms.ValidationError('El CUIL debe tener exactamente 11 dígitos.')
        return cuil
