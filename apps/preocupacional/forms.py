from django import forms
from .models import Preocupacional
from apps.informes.models import Profesional


class PreocupacionalForm(forms.ModelForm):

    class Meta:
        model  = Preocupacional
        exclude = ['fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'tarea_propuesta': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'paciente': forms.HiddenInput(),
            # Campos de texto libre para hábitos y antecedentes
            'fuma_cuantos':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'cantidad/día'}),
            'alcohol_cuanto':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'cantidad/día'}),
            'pers_abandono_causas':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Causas...'}),
            'pers_indemnizacion_causas':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Causas...'}),
            'pers_negado_causas':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Causas...'}),
            'pers_alergias_cuales':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cuáles...'}),
        }

    def __init__(self, *args, paciente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profesional'].queryset = Profesional.objects.all().order_by('apellido', 'nombre')
        self.fields['profesional'].widget.attrs['class'] = 'form-control'
        self.fields['profesional'].label = 'Profesional a cargo'
        self.fields['fecha'].input_formats = ['%Y-%m-%d']
        if paciente:
            self.fields['paciente'].initial = paciente


from .models import ExamenFisico

class ExamenFisicoForm(forms.ModelForm):
    class Meta:
        model = ExamenFisico
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'fecha', 'profesional', 'turno']
        widgets = {
            'peso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 75.5'}),
            'talla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 175'}),
            'tension_arterial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 120/80'}),
            'sat_oxigeno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 98%'}),
            'frecuencia_cardiaca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 72 lpm'}),
            'imc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 24.6'}),
            'piel_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'cabeza_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'osteo_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'visual_cromatica': forms.TextInput(attrs={'class': 'form-control'}),
            'visual_od_sc': forms.TextInput(attrs={'class': 'form-control'}),
            'visual_oi_sc': forms.TextInput(attrs={'class': 'form-control'}),
            'visual_od_cc': forms.TextInput(attrs={'class': 'form-control'}),
            'visual_oi_cc': forms.TextInput(attrs={'class': 'form-control'}),
            'neuro_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'cardio_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'resp_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'abd_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'inmuno_otras': forms.TextInput(attrs={'class': 'form-control'}),
            'odonto_data': forms.HiddenInput(),
            'odonto_observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'conclusion': forms.TextInput(attrs={'class': 'form-control'}),
        }
