from django.db import models
from apps.pacientes.models import Paciente
from apps.informes.models import Profesional


class Preocupacional(models.Model):
    """
    Registro del cuestionario preocupacional.
    Estructura exacta del formulario físico: Hábitos, Antec. Familiares,
    Antec. Personales y Antec. Médicos.
    """

    RESULTADO_CHOICES = [
        ('APTO',        'Apto'),
        ('APTO_OBS',    'Apto con Observaciones'),
        ('NO_APTO',     'No Apto'),
        ('PENDIENTE',   'Pendiente'),
    ]

    paciente    = models.ForeignKey(
                    Paciente,
                    on_delete=models.PROTECT,
                    related_name='preocupacionales',
                    verbose_name='Paciente',
                  )
    profesional = models.ForeignKey(
                    Profesional,
                    on_delete=models.PROTECT,
                    related_name='preocupacionales',
                    verbose_name='Profesional',
                  )
    fecha       = models.DateField(verbose_name='Fecha del examen')
    resultado   = models.CharField(
                    max_length=20,
                    choices=RESULTADO_CHOICES,
                    default='PENDIENTE',
                    verbose_name='Resultado',
                  )

    # ═══════════════════════════════════════════════════════════
    # A. HÁBITOS
    # ═══════════════════════════════════════════════════════════
    fuma                = models.BooleanField(default=False, verbose_name='¿Fuma?')
    fuma_cuantos        = models.CharField(max_length=100, blank=True, verbose_name='¿Cuántos por día?')
    toma_alcohol        = models.BooleanField(default=False, verbose_name='¿Toma alcohol?')
    alcohol_cuanto      = models.CharField(max_length=100, blank=True, verbose_name='¿Cuánto por día?')

    # ═══════════════════════════════════════════════════════════
    # B. ANTECEDENTES FAMILIARES (Padre - Madre)
    # ═══════════════════════════════════════════════════════════
    fam_hipertension    = models.BooleanField(default=False, verbose_name='Hipertensión Arterial')
    fam_neurologicas    = models.BooleanField(default=False, verbose_name='Neurológicas')
    fam_otras           = models.BooleanField(default=False, verbose_name='Otras')
    fam_diabetes        = models.BooleanField(default=False, verbose_name='Diabetes')
    fam_neoplasias      = models.BooleanField(default=False, verbose_name='Neoplasias')

    # ═══════════════════════════════════════════════════════════
    # C. ANTECEDENTES PERSONALES
    # ═══════════════════════════════════════════════════════════
    pers_abandono_empleo        = models.BooleanField(default=False, verbose_name='¿Tuvo que abandonar algún empleo por razones de salud?')
    pers_abandono_causas        = models.CharField(max_length=300, blank=True, verbose_name='Causas abandono empleo')
    pers_indemnizacion          = models.BooleanField(default=False, verbose_name='¿Recibió o tiene pendiente indemnización por acc. de trabajo o enf. profesional?')
    pers_indemnizacion_causas   = models.CharField(max_length=300, blank=True, verbose_name='Causas indemnización')
    pers_negado_seguro          = models.BooleanField(default=False, verbose_name='¿Le ha sido negado alguna vez un seguro de vida?')
    pers_negado_causas          = models.CharField(max_length=300, blank=True, verbose_name='Causas seguro')
    pers_alergias               = models.BooleanField(default=False, verbose_name='¿Sufre de alergias?')
    pers_alergias_cuales        = models.CharField(max_length=300, blank=True, verbose_name='Cuáles alergias')

    # ═══════════════════════════════════════════════════════════
    # D. ANTECEDENTES MÉDICOS  (columna izquierda)
    # ═══════════════════════════════════════════════════════════
    med_mareos              = models.BooleanField(default=False, verbose_name='Mareos o desmayos')
    med_convulsiones        = models.BooleanField(default=False, verbose_name='Convulsiones')
    med_pesadillas          = models.BooleanField(default=False, verbose_name='Pesadillas')
    med_neuritis            = models.BooleanField(default=False, verbose_name='Neuritis o neuralgias')
    med_depresion           = models.BooleanField(default=False, verbose_name='Depresión')
    med_fiebre_reumatica    = models.BooleanField(default=False, verbose_name='Fiebre reumática')
    med_tuberculosis        = models.BooleanField(default=False, verbose_name='Tuberculosis')
    med_asma                = models.BooleanField(default=False, verbose_name='Asma o fiebre de Heno')
    med_ulcera              = models.BooleanField(default=False, verbose_name='Úlcera gástrica o duodenal')
    med_indigestion         = models.BooleanField(default=False, verbose_name='Indigestión frecuente')
    med_glucosa_albumina    = models.BooleanField(default=False, verbose_name='Glucosa o Albúmina de orina')
    med_hemorroides         = models.BooleanField(default=False, verbose_name='Hemorroides')
    med_enf_piel            = models.BooleanField(default=False, verbose_name='Enfermedades de la piel')
    med_sordera             = models.BooleanField(default=False, verbose_name='Sordera, disminución auditiva')
    med_resfrios            = models.BooleanField(default=False, verbose_name='Resfríos frecuentes')
    med_amigdalitis         = models.BooleanField(default=False, verbose_name='Amigdalitis')
    med_sinusitis           = models.BooleanField(default=False, verbose_name='Sinusitis')
    med_sudores             = models.BooleanField(default=False, verbose_name='Sudores nocturnos')
    med_dolor_pecho         = models.BooleanField(default=False, verbose_name='Dolores de pecho')
    med_palpitaciones       = models.BooleanField(default=False, verbose_name='Palpitaciones')
    med_dificultad_orinar   = models.BooleanField(default=False, verbose_name='Dificultad para orinar')
    med_dolor_pies          = models.BooleanField(default=False, verbose_name='Dolores en pies o plano')
    med_dolor_cintura       = models.BooleanField(default=False, verbose_name='Dolores de cintura, espalda')
    med_varices             = models.BooleanField(default=False, verbose_name='Varices')
    med_diabetes            = models.BooleanField(default=False, verbose_name='Diabetes')

    # D. ANTECEDENTES MÉDICOS  (columna derecha)
    med_nerviosismo         = models.BooleanField(default=False, verbose_name='Nerviosismo excesivo')
    med_dolor_cabeza        = models.BooleanField(default=False, verbose_name='Dolores de cabeza frecuentes')
    med_perdida_memoria     = models.BooleanField(default=False, verbose_name='Pérdida de memoria')
    med_brucelosis          = models.BooleanField(default=False, verbose_name='Brucelosis')
    med_paludismo           = models.BooleanField(default=False, verbose_name='Paludismo')
    med_enf_venereas        = models.BooleanField(default=False, verbose_name='Enfermedades venéreas')
    med_cancer              = models.BooleanField(default=False, verbose_name='Cáncer u otro tumor')
    med_urticaria           = models.BooleanField(default=False, verbose_name='Urticaria')
    med_ictericia           = models.BooleanField(default=False, verbose_name='Ictericia - Hepatitis')
    med_acidez              = models.BooleanField(default=False, verbose_name='Acidez')
    med_hernias             = models.BooleanField(default=False, verbose_name='Hernias')
    med_articulaciones      = models.BooleanField(default=False, verbose_name='Articulaciones dolorosas')
    med_trastornos_ojos     = models.BooleanField(default=False, verbose_name='Trastornos en los ojos')
    med_supuracion_oidos    = models.BooleanField(default=False, verbose_name='Supuración de oídos')
    med_dentadura           = models.BooleanField(default=False, verbose_name='Dentadura en mal estado')
    med_tos_cronica         = models.BooleanField(default=False, verbose_name='Tos Crónica')
    med_sangre_esputo       = models.BooleanField(default=False, verbose_name='Sangre en esputo')
    med_perdida_peso        = models.BooleanField(default=False, verbose_name='Pérdida de peso reciente')
    med_falta_aire          = models.BooleanField(default=False, verbose_name='Falta de aire')
    med_presion_alta        = models.BooleanField(default=False, verbose_name='Presión alta')
    med_fracturas           = models.BooleanField(default=False, verbose_name='Fracturas o luxaciones')
    med_dolor_rodilla       = models.BooleanField(default=False, verbose_name='Dolores de rodilla')
    med_dolor_hombro        = models.BooleanField(default=False, verbose_name='Dolor de hombro')
    med_cirugias            = models.BooleanField(default=False, verbose_name='Cirugías')

    # ═══════════════════════════════════════════════════════════
    # OBSERVACIONES GENERALES
    # ═══════════════════════════════════════════════════════════
    tarea_propuesta     = models.CharField(max_length=300, blank=True, verbose_name='Tarea propuesta')
    observaciones       = models.TextField(blank=True, verbose_name='Observaciones')

    # METADATOS
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'ml_preocupacional'
        verbose_name        = 'Examen Preocupacional'
        verbose_name_plural = 'Exámenes Preocupacionales'
        ordering            = ['-fecha', '-fecha_creacion']

    def __str__(self):
        return f"Preocupacional {self.paciente} — {self.fecha}"


class ExamenFisico(models.Model):
    """
    Registro del examen físico presencial.
    Complementa al cuestionario preocupacional.
    """
    turno = models.OneToOneField(
        'turnos.ReservaTurno',
        on_delete=models.CASCADE,
        related_name='examen_fisico',
        verbose_name='Turno'
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name='examenes_fisicos',
        verbose_name='Profesional'
    )
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha de carga')

    # DATOS INICIALES
    peso = models.CharField(max_length=50, blank=True, verbose_name='Peso (Kg)')
    talla = models.CharField(max_length=50, blank=True, verbose_name='Talla (Cm.)')
    tension_arterial = models.CharField(max_length=50, blank=True, verbose_name='Tensión Arterial (TA)')
    sat_oxigeno = models.CharField(max_length=50, blank=True, verbose_name='Saturación de Oxígeno (Sat.O2)')
    frecuencia_cardiaca = models.CharField(max_length=50, blank=True, verbose_name='Frecuencia Cardíaca (Latidos)')
    imc = models.CharField(max_length=50, blank=True, verbose_name='Índice de Masa Corporal (IMC)')

    # PIEL
    piel_normal = models.BooleanField(default=True, verbose_name='Normal')
    piel_cicatrices = models.BooleanField(default=False, verbose_name='Cicatrices')
    piel_lesiones = models.BooleanField(default=False, verbose_name='Lesiones')
    piel_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # TCS
    tcs_normal = models.BooleanField(default=True, verbose_name='Normal')
    tcs_adenopatias = models.BooleanField(default=False, verbose_name='Adenopatías')
    tcs_edemas = models.BooleanField(default=False, verbose_name='Edemas')

    # CABEZA Y CUELLO
    cabeza_normal = models.BooleanField(default=True, verbose_name='Normal')
    cabeza_faringitis = models.BooleanField(default=False, verbose_name='Faringitis')
    cabeza_edemas = models.BooleanField(default=False, verbose_name='Edemas')
    cabeza_caries = models.BooleanField(default=False, verbose_name='Caries')
    cabeza_tiroides = models.BooleanField(default=False, verbose_name='Tiroides palpables')
    cabeza_adenopatias = models.BooleanField(default=False, verbose_name='Adenopatías')
    cabeza_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # OSTEOARTICULAR
    osteo_normal = models.BooleanField(default=True, verbose_name='Normal')
    osteo_manos = models.BooleanField(default=False, verbose_name='Manos - Deformidades')
    osteo_varices = models.BooleanField(default=False, verbose_name='Várices')
    osteo_desviaciones = models.BooleanField(default=False, verbose_name='Desviaciones de columna')
    osteo_pie_plano = models.BooleanField(default=False, verbose_name='Pie plano')
    osteo_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # AGUDEZA VISUAL
    visual_anteojos = models.BooleanField(default=False, verbose_name='Usa anteojos')
    visual_cromatica = models.CharField(max_length=100, blank=True, verbose_name='Visión cromática')
    visual_od_sc = models.CharField(max_length=50, blank=True, verbose_name='OD s/c')
    visual_oi_sc = models.CharField(max_length=50, blank=True, verbose_name='OI s/c')
    visual_od_cc = models.CharField(max_length=50, blank=True, verbose_name='OD c/c')
    visual_oi_cc = models.CharField(max_length=50, blank=True, verbose_name='OI c/c')

    # EXAMEN NEUROLÓGICO
    neuro_normal = models.BooleanField(default=True, verbose_name='Normal')
    neuro_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # APARATO CARDIOVASCULAR
    cardio_pulso = models.BooleanField(default=True, verbose_name='Pulso x min. rítmico')
    cardio_ruidos = models.BooleanField(default=True, verbose_name='Ruidos normales')
    cardio_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # APARATO RESPIRATORIO
    resp_normal = models.BooleanField(default=True, verbose_name='Auscultación normal')
    resp_sibilancias = models.BooleanField(default=False, verbose_name='Sibilancias')
    resp_rales = models.BooleanField(default=False, verbose_name='Rales')
    resp_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # ABDOMEN
    abd_normal = models.BooleanField(default=True, verbose_name='Normal')
    abd_hepatomegalia = models.BooleanField(default=False, verbose_name='Hepatomegalia')
    abd_hernia_umb = models.BooleanField(default=False, verbose_name='Hernia umbilical')
    abd_anillos_dil = models.BooleanField(default=False, verbose_name='Anillos inguinales dilatados')
    abd_anillo_der = models.BooleanField(default=False, verbose_name='Derecho')
    abd_anillo_izq = models.BooleanField(default=False, verbose_name='Izquierdo')
    abd_palpacion = models.BooleanField(default=False, verbose_name='Palpación dolorosa')
    abd_puno = models.BooleanField(default=False, verbose_name='Puño percusión positiva')
    abd_hernia_ing = models.BooleanField(default=False, verbose_name='Hernia inguinal')
    abd_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')

    # INMUNIZACIONES
    inmuno_antitetanica = models.BooleanField(default=False, verbose_name='Antitetánica')
    inmuno_antigripal = models.BooleanField(default=False, verbose_name='Antigripal')
    inmuno_otras = models.CharField(max_length=150, blank=True, verbose_name='Otras. ¿Cuál?')

    # ODONTOGRAMA
    odonto_data = models.TextField(blank=True, default='{}', verbose_name='Datos Odontograma (JSON)')
    odonto_observaciones = models.CharField(max_length=250, blank=True, verbose_name='Observaciones Odontograma')
    conclusion = models.CharField(max_length=250, blank=True, verbose_name='Conclusión')

    # METADATOS
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ml_examen_fisico'
        verbose_name = 'Examen Físico'
        verbose_name_plural = 'Exámenes Físicos'

    def __str__(self):
        return f"Examen Físico - Turno #{self.turno_id}"
