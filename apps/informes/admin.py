from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Informe, Profesional, Especialidad, FirmaDigital, PerfilProfesional


# ── Inline: Perfil Profesional dentro del formulario de Usuario ───────────────

class PerfilProfesionalInline(admin.StackedInline):
    model = PerfilProfesional
    can_delete = True
    verbose_name = 'Perfil de Profesional'
    verbose_name_plural = 'Perfil de Profesional'
    extra = 0
    min_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profesional')


class PrestadorUserAdmin(UserAdmin):
    """
    Extiende el UserAdmin estándar para mostrar el inline PerfilProfesional
    únicamente cuando el usuario pertenece al grupo PRESTADORES.
    """
    inlines = [PerfilProfesionalInline]

    def get_inline_instances(self, request, obj=None):
        """Muestra el inline solo si el usuario ya existe y está en PRESTADORES,
        o si se está creando (para poder asignarlo al guardar)."""
        if obj is None:
            # Usuario nuevo: no mostramos el inline todavía
            return []

        # Verificar si pertenece al grupo PRESTADORES
        es_prestador = obj.groups.filter(name='PRESTADORES').exists()
        if not es_prestador:
            return []

        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)


# Reemplazamos el UserAdmin por defecto con nuestra versión extendida
admin.site.unregister(User)
admin.site.register(User, PrestadorUserAdmin)


# ── Admins de modelos propios ─────────────────────────────────────────────────

@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'profesional', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'matricula', 'especialidad')
    search_fields = ('apellido', 'nombre', 'matricula')

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(FirmaDigital)
class FirmaDigitalAdmin(admin.ModelAdmin):
    list_display = ('profesional',)

@admin.register(PerfilProfesional)
class PerfilProfesionalAdmin(admin.ModelAdmin):
    list_display = ('profesional', 'user')
    search_fields = ('profesional__apellido', 'profesional__nombre', 'user__username')
    raw_id_fields = ('user',)
