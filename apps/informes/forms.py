from django import forms
from .models import Informe, Profesional
from apps.pacientes.models import Paciente


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

    class Meta:
        model = Informe
        fields = ['profesional', 'empresa', 'tipo_informe', 'texto_informe', 'archivo_pdf', 'estado']
        widgets = {
            'profesional':   forms.Select(attrs={'class': 'form-control'}),
            'empresa':       forms.Select(attrs={'class': 'form-control'}),
            'texto_informe': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'maxlength': 1024}),
            'archivo_pdf':   forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
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

        # Configurar el radio button inicial basado en si ya tiene archivo_pdf
        if self.instance and self.instance.pk:
            if self.instance.archivo_pdf:
                self.fields['tipo_informe'].initial = 'adjunto'
            else:
                self.fields['tipo_informe'].initial = 'manual'

        # Pre-cargar el paciente del turno si existe
        if turno and not (self.instance and self.instance.pk):
            self.fields['paciente_id'].initial = turno.paciente.pk

        self._profesional_fijo = profesional_fijo

    def clean(self):
        cleaned = super().clean()
        
        # Validar tipo de informe y campos relacionados
        tipo_informe = cleaned.get('tipo_informe')
        if tipo_informe == 'manual':
            if not cleaned.get('texto_informe'):
                self.add_error('texto_informe', 'El texto del informe es obligatorio cuando elige ingreso manual.')
            # Si quiere borrar el adjunto, en Django ModelForms, si el FileInput no pasa nada, se mantiene el actual.
            # No podemos borrarlo forzosamente sin más código (o con clear_checkbox), 
            # pero el usuario dijo que el sistema de impresión ya los distingue.
        elif tipo_informe == 'adjunto':
            # Vaciamos el texto si elige adjunto
            cleaned['texto_informe'] = ''
            # Para vaciar en la instancia real al guardar, necesitamos sobreescribir cleaned_data
            if not cleaned.get('archivo_pdf') and not (self.instance and self.instance.archivo_pdf):
                self.add_error('archivo_pdf', 'Debe adjuntar un archivo cuando selecciona esta opción.')

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
        return informe
