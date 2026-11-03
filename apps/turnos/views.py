from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ReservaTurno
from apps.informes.models import PerfilProfesional
from apps.pacientes.models import Paciente


def _get_profesional_del_usuario(user):
    """Retorna el Profesional asociado al usuario si existe PerfilProfesional."""
    if hasattr(user, 'perfil_profesional'):
        return user.perfil_profesional.profesional
    return None


@login_required
def reserva_turno_list(request):
    """
    Lista los turnos pedidos (estado PENDIENTE o PRESENTE).
    Si el usuario tiene perfil profesional, filtra para mostrar
    solo los turnos de sus pacientes (pacientes con los que tiene turnos o informes).
    """
    qs = (
        ReservaTurno.objects
        .select_related('paciente', 'profesional')
        .filter(estado__in=['PENDIENTE', 'PRESENTE'])
        .order_by('fecha_visita', 'hora_visita')
    )
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        # Se usa subquery para evitar DISTINCT sobre campos CLOB (TextField) en Oracle
        pacientes_ids = Paciente.objects.filter(
            Q(turnos__profesional=profesional) |
            Q(informes__profesional=profesional)
        ).values('id')
        qs = qs.filter(paciente_id__in=pacientes_ids)

    return render(request, 'turnos/reserva_list.html', {
        'turnos': qs,
    })
