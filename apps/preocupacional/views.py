from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch, Q

from apps.pacientes.models import Paciente
from apps.turnos.models import ReservaTurno
from .models import Preocupacional, ExamenFisico
from .forms import PreocupacionalForm, ExamenFisicoForm
from django.http import HttpResponse

def _get_profesional_del_usuario(user):
    """Retorna el Profesional asociado al usuario si existe PerfilProfesional."""
    if hasattr(user, 'perfil_profesional'):
        return user.perfil_profesional.profesional
    return None

# ── Agrupaciones de campos booleanos por sección ─────────────
HABITOS_BOOL = ['fuma', 'toma_alcohol']

FAM_FIELDS = [
    'fam_hipertension', 'fam_neurologicas', 'fam_otras',
    'fam_diabetes', 'fam_neoplasias',
]

PERS_ITEMS = [
    # (campo_bool, campo_texto_detalle)
    ('pers_abandono_empleo',  'pers_abandono_causas'),
    ('pers_indemnizacion',    'pers_indemnizacion_causas'),
    ('pers_negado_seguro',    'pers_negado_causas'),
    ('pers_alergias',         'pers_alergias_cuales'),
]

MED_IZQUIERDA = [
    'med_mareos', 'med_convulsiones', 'med_pesadillas', 'med_neuritis',
    'med_depresion', 'med_fiebre_reumatica', 'med_tuberculosis', 'med_asma',
    'med_ulcera', 'med_indigestion', 'med_glucosa_albumina', 'med_hemorroides',
    'med_enf_piel', 'med_sordera', 'med_resfrios', 'med_amigdalitis',
    'med_sinusitis', 'med_sudores', 'med_dolor_pecho', 'med_palpitaciones',
    'med_dificultad_orinar', 'med_dolor_pies', 'med_dolor_cintura',
    'med_varices', 'med_diabetes',
]
MED_DERECHA = [
    'med_nerviosismo', 'med_dolor_cabeza', 'med_perdida_memoria',
    'med_brucelosis', 'med_paludismo', 'med_enf_venereas', 'med_cancer',
    'med_urticaria', 'med_ictericia', 'med_acidez', 'med_hernias',
    'med_articulaciones', 'med_trastornos_ojos', 'med_supuracion_oidos',
    'med_dentadura', 'med_tos_cronica', 'med_sangre_esputo',
    'med_perdida_peso', 'med_falta_aire', 'med_presion_alta',
    'med_fracturas', 'med_dolor_rodilla', 'med_dolor_hombro', 'med_cirugias',
]


def _form_context(form):
    """Devuelve el contexto con campos agrupados para el template."""
    pers_items_ctx = [
        (form[bool_f], form[text_f]) for bool_f, text_f in PERS_ITEMS
    ]
    return {
        'habitos_bool':  [form[f] for f in HABITOS_BOOL],
        'fuma_cuantos':  form['fuma_cuantos'],
        'alcohol_cuanto': form['alcohol_cuanto'],
        'fam_fields':    [form[f] for f in FAM_FIELDS],
        'pers_items':    pers_items_ctx,
        'med_izquierda': [form[f] for f in MED_IZQUIERDA],
        'med_derecha':   [form[f] for f in MED_DERECHA],
    }


@staff_member_required
def preocupacional_list(request):
    """
    Listado de pacientes con su último turno, profesional y empresa.
    """
    q = request.GET.get('q', '').strip()
    qs = Paciente.objects.select_related('empresa')
    
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        pacientes_ids = Paciente.objects.filter(
            Q(turnos__profesional=profesional) |
            Q(preocupacionales__profesional=profesional)
        ).values('id')
        qs = qs.filter(id__in=pacientes_ids)

    if q:
        qs = qs.filter(Q(apellido__icontains=q) | Q(nombres__icontains=q) | Q(dni__icontains=q))

    qs = qs.prefetch_related(
        Prefetch(
            'turnos',
            queryset=ReservaTurno.objects.select_related('profesional').order_by('-fecha_visita'),
            to_attr='turnos_list',
        ),
        Prefetch(
            'preocupacionales',
            queryset=Preocupacional.objects.select_related('profesional').order_by('-fecha'),
            to_attr='examenes_list',
        ),
    ).order_by('apellido', 'nombres')

    return render(request, 'preocupacional/preocupacional_list.html', {
        'pacientes': qs,
        'q': q,
    })


@staff_member_required
def preocupacional_create(request, pk_paciente):
    """Crea un nuevo examen preocupacional para el paciente dado."""
    paciente = get_object_or_404(Paciente, pk=pk_paciente)

    if request.method == 'POST':
        form = PreocupacionalForm(request.POST, paciente=paciente)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.paciente = paciente
            exam.save()
            messages.success(request, f'Examen preocupacional de {paciente} guardado correctamente.')
            return redirect('preocupacional:preocupacional_list')
    else:
        form = PreocupacionalForm(paciente=paciente)

    ctx = {'form': form, 'paciente': paciente, 'action': 'Crear'}
    ctx.update(_form_context(form))
    return render(request, 'preocupacional/preocupacional_form.html', ctx)


@staff_member_required
def preocupacional_edit(request, pk):
    """Edita un examen preocupacional existente."""
    exam     = get_object_or_404(Preocupacional, pk=pk)
    paciente = exam.paciente

    if request.method == 'POST':
        form = PreocupacionalForm(request.POST, instance=exam, paciente=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Examen preocupacional de {paciente} actualizado.')
            return redirect('preocupacional:preocupacional_list')
    else:
        form = PreocupacionalForm(instance=exam, paciente=paciente)

    ctx = {'form': form, 'paciente': paciente, 'action': 'Editar'}
    ctx.update(_form_context(form))
    return render(request, 'preocupacional/preocupacional_form.html', ctx)




@staff_member_required
def examen_fisico_list(request):
    """
    Lista de turnos para el Examen Clínico.
    Muestra turnos ordenados por fecha y permite cargar/imprimir el examen.
    """
    q = request.GET.get('q', '').strip()
    qs = ReservaTurno.objects.select_related('paciente', 'profesional', 'examen_fisico').order_by('-fecha_visita', '-hora_visita')
    
    profesional = _get_profesional_del_usuario(request.user)
    if profesional:
        qs = qs.filter(profesional=profesional)
        
    if q:
        qs = qs.filter(
            Q(paciente__apellido__icontains=q) | 
            Q(paciente__nombres__icontains=q) | 
            Q(paciente__dni__icontains=q)
        )
        
    return render(request, 'preocupacional/examen_fisico_list.html', {
        'turnos': qs,
        'q': q,
    })

@staff_member_required
def examen_fisico_form_view(request, turno_id):
    turno = get_object_or_404(ReservaTurno, pk=turno_id)
    try:
        examen = turno.examen_fisico
    except ExamenFisico.DoesNotExist:
        examen = None
        
    if request.method == 'POST':
        form = ExamenFisicoForm(request.POST, instance=examen)
        if form.is_valid():
            nuevo_examen = form.save(commit=False)
            if not examen:
                nuevo_examen.turno = turno
                prof = _get_profesional_del_usuario(request.user)
                if not prof:
                    prof = turno.profesional
                nuevo_examen.profesional = prof
            nuevo_examen.save()
            messages.success(request, 'Examen Clínico guardado exitosamente.')
            return redirect('preocupacional:examen_fisico_list')
    else:
        form = ExamenFisicoForm(instance=examen)
        
    return render(request, 'preocupacional/examen_fisico_form.html', {
        'form': form,
        'turno': turno,
        'examen': examen
    })

@staff_member_required
def examen_fisico_pdf(request, pk):
    examen = get_object_or_404(ExamenFisico, pk=pk)
    from .pdf_services import generar_pdf_examen_fisico
    pdf_bytes = generar_pdf_examen_fisico(examen)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"examen_clinico_{examen.turno.paciente.dni}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@staff_member_required
def preocupacional_pdf(request, pk):
    preoc = get_object_or_404(Preocupacional, pk=pk)
    
    # Intentar buscar el examen físico que corresponde al mismo paciente y fecha,
    # O más bien, al último turno del paciente.
    # Dado que no hay relación directa, buscamos el examen físico más reciente del paciente.
    examen_fisico = ExamenFisico.objects.filter(turno__paciente=preoc.paciente).order_by('-turno__fecha_visita').first()
    
    from .pdf_services import generar_pdf_informe_preocupacional
    pdf_bytes = generar_pdf_informe_preocupacional(preoc, examen_fisico)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"preocupacional_completo_{preoc.paciente.dni}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
