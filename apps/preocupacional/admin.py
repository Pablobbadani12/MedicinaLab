from django.contrib import admin
from .models import Preocupacional


@admin.register(Preocupacional)
class PreocupacionalAdmin(admin.ModelAdmin):
    list_display  = ('paciente', 'profesional', 'fecha', 'resultado', 'fecha_creacion')
    list_filter   = ('resultado', 'fecha', 'profesional')
    search_fields = ('paciente__apellido', 'paciente__nombres', 'paciente__dni')
    date_hierarchy = 'fecha'
    ordering      = ('-fecha',)
