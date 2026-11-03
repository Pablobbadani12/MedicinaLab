from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Paciente
from .forms import PacienteForm


def es_supervisor(user):
    """
    Verifica si el usuario tiene rol de supervisor o administrador:
    - Superusuarios (is_superuser)
    - Personal de staff (is_staff)
    - Miembros del grupo 'SUPERVISORES' o 'SUPERVISOR'
    """
    if not user or not user.is_authenticated:
        return False
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name__in=['SUPERVISORES', 'SUPERVISOR', 'supervisores', 'supervisor']).exists()
    )


@login_required
def paciente_list(request):
    q = request.GET.get('q', '').strip()
    qs = Paciente.objects.all()

    from apps.informes.views import _get_profesional_del_usuario
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        pacientes_ids = Paciente.objects.filter(
            Q(turnos__profesional=profesional) |
            Q(informes__profesional=profesional) |
            Q(preocupacionales__profesional=profesional)
        ).values('id')
        qs = qs.filter(id__in=pacientes_ids)

    if q:
        qs = qs.filter(
            Q(apellido__icontains=q) |
            Q(nombres__icontains=q)  |
            Q(dni__icontains=q)
        )

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pacientes/paciente_list.html', {
        'pacientes':     page_obj,
        'page_obj':      page_obj,
        'q':             q,
        'es_supervisor': es_supervisor(request.user),
    })


@login_required
def paciente_detail(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    from apps.informes.models import Informe
    informes = Informe.objects.filter(paciente=paciente).select_related('profesional', 'empresa')
    return render(request, 'pacientes/paciente_detail.html', {
        'paciente': paciente,
        'informes': informes,
    })


@login_required
def paciente_create(request):
    if not es_supervisor(request.user):
        messages.error(request, 'No tiene permisos para agregar pacientes. Esta acción es solo para supervisores.')
        return redirect('pacientes:paciente_list')

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente {paciente.apellido}, {paciente.nombres} creado exitosamente.')
            return redirect('pacientes:paciente_detail', pk=paciente.pk)
    else:
        form = PacienteForm()
    return render(request, 'pacientes/paciente_form.html', {
        'form': form,
        'action': 'Nuevo',
    })


@login_required
def paciente_edit(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente.')
            return redirect('pacientes:paciente_detail', pk=paciente.pk)
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/paciente_form.html', {
        'form': form,
        'action': 'Editar',
        'paciente': paciente,
    })


@login_required
def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        nombre = str(paciente)
        paciente.delete()
        messages.success(request, f'Paciente {nombre} eliminado correctamente.')
        return redirect('pacientes:paciente_list')
    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})


@login_required
def paciente_search_json(request):
    """Endpoint AJAX: busca pacientes y devuelve JSON para el selector de informes."""
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    qs = Paciente.objects.all()

    from apps.informes.views import _get_profesional_del_usuario
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        pacientes_ids = Paciente.objects.filter(
            Q(turnos__profesional=profesional) |
            Q(informes__profesional=profesional) |
            Q(preocupacionales__profesional=profesional)
        ).values('id')
        qs = qs.filter(id__in=pacientes_ids)

    qs = qs.filter(
        Q(apellido__icontains=q) |
        Q(nombres__icontains=q)  |
        Q(dni__icontains=q)
    )[:30]

    results = [
        {
            'id':     p.pk,
            'nombre': f"{p.apellido}, {p.nombres}",
            'dni':    p.dni,
            'email':  p.email,
        }
        for p in qs
    ]
    return JsonResponse({'results': results})
