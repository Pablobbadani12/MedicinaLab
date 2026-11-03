from django.contrib import admin
from django.forms import ModelChoiceField
from .models import ReservaTurno
from apps.informes.models import Profesional


class ProfesionalChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.especialidad:
            return f"Dr/a. {obj.apellido}, {obj.nombre} - {obj.especialidad.nombre}"
        return f"Dr/a. {obj.apellido}, {obj.nombre}"


@admin.register(ReservaTurno)
class ReservaTurnoAdmin(admin.ModelAdmin):
    list_display  = ('paciente', 'fecha_visita', 'hora_visita', 'profesional', 'estado', 'fecha_creacion')
    list_filter   = ('estado', 'fecha_visita', 'profesional')
    search_fields = (
        'paciente__apellido', 'paciente__nombres', 'paciente__dni',
        'profesional__apellido', 'profesional__nombre',
    )
    ordering      = ('fecha_visita', 'hora_visita')
    date_hierarchy = 'fecha_visita'
    list_editable  = ('estado',)
    fieldsets = (
        ('Datos del Turno', {
            'fields': ('paciente', 'profesional', 'fecha_visita', 'hora_visita'),
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente', 'profesional')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profesional":
            kwargs["form_class"] = ProfesionalChoiceField
            kwargs["queryset"] = Profesional.objects.select_related('especialidad').all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

