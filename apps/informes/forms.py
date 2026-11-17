from django import forms
from django.core.validators import FileExtensionValidator
from .models import Informe, Profesional
from apps.pacientes.models import Paciente


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'widget',
            MultipleFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'multiple': True,
            }),
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data if d]
        elif data:
            return [single_file_clean(data, initial)]
        return []


class InformeForm(forms.ModelForm):
    # Campo oculto que recibe el ID del paciente desde el selector AJAX
    paciente_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_paciente_id_oracle'}),
    )

    tipo_informe = forms.ChoiceField(
        choices=[('manual', '✏️ Ingreso Manual (Texto)'), ('adjunto', '📎 Documento Adjunto (PDF/Imagen)')],
        widget=forms.RadioSelect(attrs={'class': 'tipo-informe-radio'}),
        initial='manual',
        label='Método de carga del informe'
    )

    archivo_pdf = MultipleFileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        label='Documentos Clínicos Respaldatorios (PDF / Imagen)',
    )

    class Meta:
        model = Informe
        fields = ['profesional', 'empresa', 'tipo_informe', 'texto_informe', 'estado']
        widgets = {
            'profesional':   forms.Select(attrs={'class': 'form-control'}),
            'empresa':       forms.Select(attrs={'class': 'form-control'}),
            'texto_informe': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'maxlength': 1024}),
            'estado':        forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, profesional_fijo=None, turno=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['texto_informe'].required = False
        self.fields['archivo_pdf'].required = False

        self._turno = turno

        # Si el usuario tiene un profesional asociado, limitamos el queryset
        if profesional_fijo:
            self.fields['profesional'].queryset = Profesional.objects.filter(pk=profesional_fijo.pk)
            self.fields['profesional'].initial = profesional_fijo

        # Si viene con turno, el profesional viene del turno
        if turno and not profesional_fijo:
            self.fields['profesional'].queryset = Profesional.objects.filter(pk=turno.profesional.pk)
            self.fields['profesional'].initial = turno.profesional

        # Pre-cargar el valor del paciente actual en el campo oculto
        if self.instance and self.instance.pk and self.instance.paciente_id:
            self.fields['paciente_id'].initial = self.instance.paciente_id

        # Configurar el radio button inicial basado en si ya tiene archivos adjuntos
        if self.instance and self.instance.pk:
            if self.instance.tiene_archivos_adjuntos or self.instance.archivo_pdf:
                self.fields['tipo_informe'].initial = 'adjunto'
            else:
                self.fields['tipo_informe'].initial = 'manual'

        # Pre-cargar el paciente del turno si existe
        if turno and not (self.instance and self.instance.pk):
            self.fields['paciente_id'].initial = turno.paciente.pk

        self._profesional_fijo = profesional_fijo

    def clean(self):
        cleaned = super().clean()

        tipo_informe = cleaned.get('tipo_informe')
        nuevos_archivos = cleaned.get('archivo_pdf') or []
        eliminar_keys = set(self.data.getlist('eliminar_adjuntos'))

        adjuntos_actuales = []
        if self.instance and self.instance.pk:
            adjuntos_actuales = [
                a for a in self.instance.archivos_adjuntos
                if a['key'] not in eliminar_keys
            ]

        if tipo_informe == 'manual':
            if not cleaned.get('texto_informe'):
                self.add_error('texto_informe', 'El texto del informe es obligatorio cuando elige ingreso manual.')
        elif tipo_informe == 'adjunto':
            cleaned['texto_informe'] = ''
            if not nuevos_archivos and not adjuntos_actuales:
                self.add_error('archivo_pdf', 'Debe adjuntar al menos un archivo cuando selecciona esta opción.')

        pid = cleaned.get('paciente_id') or self.data.get('paciente_id_oracle')
        if pid:
            try:
                cleaned['paciente'] = Paciente.objects.get(pk=int(pid))
            except (Paciente.DoesNotExist, ValueError):
                self.add_error(None, f'No existe un paciente con ID {pid}.')
        else:
            cleaned['paciente'] = self.instance.paciente if self.instance.pk else None
        return cleaned

    def save(self, commit=True):
        informe = super().save(commit=False)
        informe.paciente = self.cleaned_data.get('paciente')
        # Vincular el turno si fue pasado al formulario
        if self._turno:
            informe.turno = self._turno
        if commit:
            informe.save()
            eliminar_keys = self.data.getlist('eliminar_adjuntos')
            if eliminar_keys:
                informe.eliminar_archivos_adjuntos(eliminar_keys)
            nuevos_archivos = self.cleaned_data.get('archivo_pdf') or []
            if nuevos_archivos:
                informe.agregar_archivos_adjuntos(nuevos_archivos)
        return informe
