from django.contrib import admin
from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display  = ('apellido', 'nombres', 'dni', 'cuil', 'empresa', 'sexo', 'estado_civil', 'email')
    search_fields = ('apellido', 'nombres', 'dni', 'cuil')
    list_filter   = ('sexo', 'estado_civil', 'empresa')
    ordering      = ('apellido', 'nombres')
