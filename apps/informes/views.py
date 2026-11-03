from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q
import hashlib
import json
from .models import Informe, PerfilProfesional, FirmaDigital
from apps.pacientes.models import Paciente
from apps.turnos.models import ReservaTurno
from .forms import InformeForm
from .services import generar_pdf_consolidado, generar_pdf_informe


def _get_profesional_del_usuario(user):
    """
    Retorna el Profesional asociado al usuario si existe PerfilProfesional,
    de lo contrario retorna None (usuario admin/sin restricción).
    """
    try:
        return user.perfil_profesional.profesional
    except PerfilProfesional.DoesNotExist:
        return None
    except AttributeError:
        return None


@login_required
def informe_list(request):
    qs = Informe.objects.select_related('profesional', 'empresa', 'paciente').all()
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        # Se usa subquery para evitar DISTINCT sobre campos CLOB (TextField) en Oracle
        pacientes_ids = Paciente.objects.filter(
            Q(turnos__profesional=profesional) |
            Q(informes__profesional=profesional)
        ).values('id')
        qs = qs.filter(paciente_id__in=pacientes_ids)
    return render(request, 'informes/informe_list.html', {'informes': qs})


@login_required
def informe_create(request):
    profesional = _get_profesional_del_usuario(request.user)

    # Soporte para crear informe desde un turno: heredar paciente y profesional
    turno = None
    turno_id = request.GET.get('turno_id') or request.POST.get('turno_id')
    if turno_id:
        turno = get_object_or_404(ReservaTurno, pk=turno_id)
        # Si el usuario es profesional y el turno no le pertenece, bloqueamos
        if profesional and turno.profesional != profesional:
            messages.error(request, 'No tenés permiso para crear un informe sobre este turno.')
            return redirect('turnos:reserva_list')
        # Si el usuario es admin (sin profesional fijo), usamos el del turno
        if not profesional:
            profesional_para_form = turno.profesional
        else:
            profesional_para_form = profesional
    else:
        profesional_para_form = profesional

    # Inicializar paciente_nombre siempre, para evitar UnboundLocalError
    # si el formulario POST resulta inválido y se re-renderiza el template.
    paciente_nombre = ''
    if turno:
        paciente_nombre = f"{turno.paciente.apellido}, {turno.paciente.nombres}"

    if request.method == 'POST':
        form = InformeForm(
            request.POST, request.FILES,
            profesional_fijo=profesional_para_form,
            turno=turno,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Informe creado exitosamente.')
            return redirect('informes:informe_list')
    else:
        initial = {}
        if turno:
            initial['paciente_id'] = turno.paciente.pk
        form = InformeForm(
            profesional_fijo=profesional_para_form,
            turno=turno,
            initial=initial,
        )

    context = {
        'form': form,
        'action': 'Crear',
        'paciente_nombre': paciente_nombre,
        'profesional_fijo': profesional_para_form,
        'turno': turno,
    }
    return render(request, 'informes/informe_form.html', context)


@login_required
def informe_edit(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    # Si el usuario es profesional, sólo puede editar sus propios informes
    profesional = _get_profesional_del_usuario(request.user)
    if profesional and informe.profesional != profesional:
        messages.error(request, 'No tenés permiso para editar este informe.')
        return redirect('informes:informe_list')

    if informe.estado == 'FINALIZADO':
        messages.error(request, 'Este informe esta finalizado y no puede ser modificado.')
        return redirect('informes:informe_detail', pk=pk)

    paciente_nombre = ''
    if informe.paciente:
        p = informe.paciente
        paciente_nombre = f"{p.apellido}, {p.nombres}"

    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES, instance=informe, profesional_fijo=profesional)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informe actualizado.')
            return redirect('informes:informe_list')
        else:
            try:
                pid = int(request.POST.get('paciente_id_oracle', 0))
                p = Paciente.objects.get(pk=pid)
                paciente_nombre = f"{p.apellido}, {p.nombres}"
            except Exception:
                pass
    else:
        form = InformeForm(instance=informe, profesional_fijo=profesional)
    return render(request, 'informes/informe_form.html', {
        'form': form,
        'action': 'Editar',
        'paciente_nombre': paciente_nombre,
        'profesional_fijo': profesional,
    })


@login_required
def informe_detail(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    # Si el usuario es profesional, sólo puede ver sus propios informes
    profesional = _get_profesional_del_usuario(request.user)
    if profesional and informe.profesional != profesional:
        messages.error(request, 'No tenés permiso para ver este informe.')
        return redirect('informes:informe_list')

    return render(request, 'informes/informe_detail.html', {'informe': informe})


@login_required
def informe_delete(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    # Si el usuario es profesional, sólo puede eliminar sus propios informes
    profesional = _get_profesional_del_usuario(request.user)
    if profesional and informe.profesional != profesional:
        messages.error(request, 'No tenés permiso para eliminar este informe.')
        return redirect('informes:informe_list')

    if request.method == 'POST':
        informe.delete()
        messages.success(request, 'Informe eliminado correctamente.')
        return redirect('informes:informe_list')
    return render(request, 'informes/informe_confirm_delete.html', {'informe': informe})


@login_required
def imprimir_consolidado(request, pk_paciente):
    paciente = get_object_or_404(Paciente, pk=pk_paciente)
    informes = Informe.objects.filter(paciente=paciente).select_related('profesional')
    pdf_buffer = generar_pdf_consolidado(paciente, informes)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="consolidado_{paciente.dni}.pdf"'
    # Evitar caché del navegador
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
def imprimir_informe(request, pk):
    informe = get_object_or_404(Informe, pk=pk)
    pdf_bytes = generar_pdf_informe(informe)
    paciente = informe.paciente
    apellido = (paciente.apellido or 'paciente').replace(' ', '_') if paciente else 'paciente'
    filename = f"informe_{informe.id}_{apellido}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    # Evitar que el browser cachee el PDF y muestre siempre el del informe anterior
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
@require_POST
def verificar_firma(request, pk):
    """
    Endpoint AJAX: valida el PIN del profesional (comparando SHA-256)
    y, si es correcto, finaliza el informe registrando firma_timestamp.
    """
    informe = get_object_or_404(Informe, pk=pk)

    # Control de permisos
    profesional = _get_profesional_del_usuario(request.user)
    if profesional and informe.profesional != profesional:
        return JsonResponse({'ok': False, 'error': 'Sin permiso para firmar este informe.'}, status=403)

    if informe.estado == 'FINALIZADO':
        return JsonResponse({'ok': False, 'error': 'El informe ya está finalizado.'}, status=400)

    try:
        body = json.loads(request.body)
        pin = body.get('pin', '')
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'ok': False, 'error': 'Petición inválida.'}, status=400)

    if not pin:
        return JsonResponse({'ok': False, 'error': 'Debe ingresar el PIN.'})

    # Obtener la FirmaDigital del profesional del informe
    try:
        firma_digital = FirmaDigital.objects.get(profesional=informe.profesional)
    except FirmaDigital.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'El profesional no tiene una firma digital configurada. Configure una desde el panel de administración.'})

    # Comparar SHA-256 del PIN ingresado con el hash almacenado
    pin_hash = hashlib.sha256(pin.encode('utf-8')).hexdigest()
    if pin_hash != firma_digital.hash_firma:
        return JsonResponse({'ok': False, 'error': 'PIN incorrecto. Intente nuevamente.'})

    # Guardar el informe como FINALIZADO (bypass de clean() para evitar loop)
    Informe.objects.filter(pk=informe.pk).update(
        estado='FINALIZADO',
        firma_timestamp=timezone.now(),
    )

    return JsonResponse({'ok': True, 'redirect': f'/informes/{informe.pk}/'})
