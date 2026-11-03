import io
import os
import json
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, Polygon, Line, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def _yes_no(value):
    return "[ X ]" if value else "[   ]"

def generar_dibujo_odontograma(odonto_data_raw):
    """
    Genera un Drawing de ReportLab con el Odontograma FDI (32 piezas dentales),
    mostrando las 5 caras por pieza con sus respectivos colores y marcas de estado.
    Retorna (drawing, summary_text).
    """
    if isinstance(odonto_data_raw, str):
        try:
            odonto_data = json.loads(odonto_data_raw) if odonto_data_raw.strip() else {}
        except Exception:
            odonto_data = {}
    elif isinstance(odonto_data_raw, dict):
        odonto_data = odonto_data_raw
    else:
        odonto_data = {}

    d = Drawing(470, 88)

    quad_1 = [18, 17, 16, 15, 14, 13, 12, 11]
    quad_2 = [21, 22, 23, 24, 25, 26, 27, 28]
    quad_4 = [48, 47, 46, 45, 44, 43, 42, 41]
    quad_3 = [31, 32, 33, 34, 35, 36, 37, 38]

    tooth_size = 22
    tooth_gap = 4
    quad_width = 8 * tooth_size + 7 * tooth_gap
    center_gap = 18
    start_x = (470 - (quad_width * 2 + center_gap)) / 2
    x_center = start_x + quad_width + (center_gap / 2)

    y_upper = 49
    y_lower = 17
    y_mid = 44

    c_caries = colors.HexColor('#EF4444')
    c_obturado = colors.HexColor('#3B82F6')
    c_white = colors.HexColor('#FFFFFF')
    c_border = colors.HexColor('#475569')
    c_ausente = colors.HexColor('#DC2626')
    c_corona = colors.HexColor('#F59E0B')
    c_line = colors.HexColor('#0F766E')

    # Líneas divisorias en cruz (+)
    d.add(Line(start_x - 6, y_mid, start_x + quad_width * 2 + center_gap + 6, y_mid, strokeColor=c_line, strokeWidth=1.5))
    d.add(Line(x_center, 8, x_center, 80, strokeColor=c_line, strokeWidth=1.5))

    caries_list = []
    obturado_list = []
    ausente_list = []
    corona_list = []

    def draw_tooth(x0, y0, num, is_upper_arch):
        str_num = str(num)
        t_data = odonto_data.get(str_num, {})
        status = t_data.get('status')

        x1 = x0 + tooth_size
        y1 = y0 + tooth_size

        num_y = y1 + 3 if is_upper_arch else y0 - 8
        d.add(String(x0 + (tooth_size / 2), num_y, str_num, fontName='Helvetica-Bold', fontSize=7, textAnchor='middle', fillColor=colors.HexColor('#334155')))

        ix0 = x0 + 6
        iy0 = y0 + 6
        ix1 = x1 - 6
        iy1 = y1 - 6

        surfaces = [
            ('T', [x0, y1, x1, y1, ix1, iy1, ix0, iy1]),
            ('B', [x0, y0, ix0, iy0, ix1, iy0, x1, y0]),
            ('L', [x0, y0, x0, y1, ix0, iy1, ix0, iy0]),
            ('R', [x1, y0, ix1, iy0, ix1, iy1, x1, y1]),
            ('C', [ix0, iy0, ix1, iy0, ix1, iy1, ix0, iy1])
        ]

        if status == 'ausente':
            ausente_list.append(str_num)
        if status == 'corona':
            corona_list.append(str_num)

        for s_id, pts in surfaces:
            s_val = t_data.get(s_id)
            if status == 'ausente':
                fill = colors.HexColor('#F3F4F6')
            elif s_val == 'caries':
                fill = c_caries
                caries_list.append(f"{str_num}-{s_id}")
            elif s_val == 'obturado':
                fill = c_obturado
                obturado_list.append(f"{str_num}-{s_id}")
            else:
                fill = c_white
            d.add(Polygon(pts, fillColor=fill, strokeColor=c_border, strokeWidth=0.5))

        if status == 'ausente':
            d.add(Line(x0 + 1, y0 + 1, x1 - 1, y1 - 1, strokeColor=c_ausente, strokeWidth=1.8))
            d.add(Line(x0 + 1, y1 - 1, x1 - 1, y0 + 1, strokeColor=c_ausente, strokeWidth=1.8))
        elif status == 'corona':
            d.add(Rect(x0 - 1.5, y0 - 1.5, tooth_size + 3, tooth_size + 3, fillColor=None, strokeColor=c_corona, strokeWidth=1.6, rx=2, ry=2))

    for idx, num in enumerate(quad_1):
        x = start_x + idx * (tooth_size + tooth_gap)
        draw_tooth(x, y_upper, num, True)

    x_q2 = x_center + (center_gap / 2)
    for idx, num in enumerate(quad_2):
        x = x_q2 + idx * (tooth_size + tooth_gap)
        draw_tooth(x, y_upper, num, True)

    for idx, num in enumerate(quad_4):
        x = start_x + idx * (tooth_size + tooth_gap)
        draw_tooth(x, y_lower, num, False)

    for idx, num in enumerate(quad_3):
        x = x_q2 + idx * (tooth_size + tooth_gap)
        draw_tooth(x, y_lower, num, False)

    parts = []
    if ausente_list:
        parts.append(f"<b>Piezas ausentes:</b> {', '.join(ausente_list)}")
    if caries_list:
        parts.append(f"<b>Caries:</b> {', '.join(caries_list)}")
    if obturado_list:
        parts.append(f"<b>Obturaciones:</b> {', '.join(obturado_list)}")
    if corona_list:
        parts.append(f"<b>Coronas/Prótesis:</b> {', '.join(corona_list)}")

    if parts:
        summary_text = " • ".join(parts)
    else:
        summary_text = "<b>Hallazgos:</b> Dentadura completa sin patologías registradas en gráfico."

    return d, summary_text

def generar_pdf_examen_fisico(examen):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    section_title_style = ParagraphStyle(
        'SectionTitleStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.white,
        backColor=colors.HexColor('#E58E73'),
        spaceBefore=10,
        spaceAfter=10,
        leftIndent=5,
        rightIndent=5,
        borderPadding=4,
    )
    
    normal_style = styles['Normal']
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 9
    
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

    elements = []
    
    # 1. Header
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=150, height=45, hAlign='LEFT'))
        elements.append(Spacer(1, 5))
    
    from reportlab.platypus import HRFlowable
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#DC5F43'), spaceAfter=20))
    
    # 2. Patient Data
    paciente = examen.turno.paciente
    
    from datetime import date
    edad = "—"
    if paciente and paciente.fecnaci:
        today = date.today()
        edad_num = today.year - paciente.fecnaci.year - ((today.month, today.day) < (paciente.fecnaci.month, paciente.fecnaci.day))
        edad = str(edad_num)

    nombre = f"{paciente.nombres or ''} {paciente.apellido or ''}".strip() if paciente else "—"
    dni = paciente.dni if paciente else "—"
    fecha = examen.turno.fecha.strftime("%d/%m/%Y") if hasattr(examen, 'turno') and hasattr(examen.turno, 'fecha') else date.today().strftime("%d/%m/%Y")

    datos_paciente = [
        [Paragraph("<b>Nombre y Apellido:</b>", normal_style), Paragraph(nombre, normal_style)],
        [Paragraph("<b>Edad:</b>", normal_style), Paragraph(edad, normal_style)],
        [Paragraph("<b>DNI:</b>", normal_style), Paragraph(str(dni), normal_style)],
        [Paragraph("<b>Fecha:</b>", normal_style), Paragraph(fecha, normal_style)],
    ]

    t_paciente = Table(datos_paciente, colWidths=[100, 400], hAlign='LEFT')
    t_paciente.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(t_paciente)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#DC5F43'), spaceBefore=5, spaceAfter=15))

    # Medidas / Signos Vitales (Datos Iniciales)
    peso_val = getattr(examen, 'peso', '') or '—'
    talla_val = getattr(examen, 'talla', '') or '—'
    ta_val = getattr(examen, 'tension_arterial', '') or '—'
    sat_val = getattr(examen, 'sat_oxigeno', '') or '—'
    fc_val = getattr(examen, 'frecuencia_cardiaca', '') or '—'
    imc_val = getattr(examen, 'imc', '') or '—'

    datos_medidas = [
        [
            Paragraph(f"<b>A. Peso (Kg):</b> {peso_val}", normal_style),
            Paragraph(f"<b>B. Talla (Cm.):</b> {talla_val}", normal_style),
            Paragraph(f"<b>C. Tensión Arterial (TA):</b> {ta_val}", normal_style),
        ],
        [
            Paragraph(f"<b>D. Sat. O2:</b> {sat_val}", normal_style),
            Paragraph(f"<b>E. Frec. Cardíaca:</b> {fc_val}", normal_style),
            Paragraph(f"<b>F. IMC:</b> {imc_val}", normal_style),
        ]
    ]
    t_medidas = Table(datos_medidas, colWidths=[178, 178, 179], hAlign='LEFT')
    t_medidas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("<b>Datos Iniciales:</b>", ParagraphStyle('DatosIniTitle', parent=normal_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1E293B'))))
    elements.append(Spacer(1, 4))
    elements.append(t_medidas)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("<b>Informe:</b>", ParagraphStyle('InformeStyle', parent=normal_style, fontName='Helvetica-Bold', fontSize=10)))
    elements.append(Spacer(1, 10))

    # Helper function for drawing exam sections
    def create_section(title, fields, obs=None):
        section_elements = []
        section_elements.append(Paragraph(title, section_title_style))
        
        # Fields is a list of tuples (Label, BooleanValue)
        # We will group them in pairs (2 columns per row)
        rows = []
        current_row = []
        for label, val in fields:
            current_row.extend([Paragraph(label, normal_style), Paragraph(_yes_no(val), normal_style)])
            if len(current_row) == 4:
                rows.append(current_row)
                current_row = []
        if current_row:
            current_row.extend(["", ""])
            rows.append(current_row)
            
        if rows:
            t_fields = Table(rows, colWidths=[150, 117, 150, 118])
            t_fields.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
            ]))
            section_elements.append(t_fields)
            
        if obs:
            section_elements.append(Spacer(1, 5))
            obs_text = str(obs).strip() if str(obs).strip() else "Sin observaciones."
            section_elements.append(Paragraph(f"<b>Observaciones:</b> {obs_text}", normal_style))
            
        section_elements.append(Spacer(1, 10))
        return KeepTogether(section_elements)

    # 3. Exam Sections
    # PIEL
    elements.append(create_section("PIEL", [
        ("Normal", examen.piel_normal),
        ("Cicatrices", examen.piel_cicatrices),
        ("Lesiones", examen.piel_lesiones)
    ], examen.piel_observaciones))

    # TCS
    elements.append(create_section("TEJIDO CELULAR SUBCUTÁNEO (TCS)", [
        ("Normal", examen.tcs_normal),
        ("Adenopatías", examen.tcs_adenopatias),
        ("Edemas", examen.tcs_edemas)
    ]))

    # CABEZA Y CUELLO
    elements.append(create_section("CABEZA Y CUELLO", [
        ("Normal", examen.cabeza_normal),
        ("Caries", examen.cabeza_caries),
        ("Faringitis", examen.cabeza_faringitis),
        ("Tiroides", examen.cabeza_tiroides),
        ("Edemas", examen.cabeza_edemas),
        ("Adenopatías", examen.cabeza_adenopatias)
    ], examen.cabeza_observaciones))

    # OSTEOARTICULAR
    elements.append(create_section("OSTEOARTICULAR", [
        ("Normal", examen.osteo_normal),
        ("Desviaciones", examen.osteo_desviaciones),
        ("Manos", examen.osteo_manos),
        ("Pie plano", examen.osteo_pie_plano),
        ("Várices", examen.osteo_varices)
    ], examen.osteo_observaciones))
    
    # EXAMEN NEUROLOGICO
    elements.append(create_section("EXAMEN NEUROLÓGICO", [
        ("Normal", examen.neuro_normal)
    ], examen.neuro_observaciones))

    # CARDIOVASCULAR
    elements.append(create_section("CARDIOVASCULAR", [
        ("Pulso", examen.cardio_pulso),
        ("Ruidos", examen.cardio_ruidos)
    ], examen.cardio_observaciones))

    # RESPIRATORIO
    elements.append(create_section("RESPIRATORIO", [
        ("Normal", examen.resp_normal),
        ("Sibilancias", examen.resp_sibilancias),
        ("Rales", examen.resp_rales)
    ], examen.resp_observaciones))

    # ABDOMEN
    abd_fields = [
        ("Normal", examen.abd_normal),
        ("Palpación", examen.abd_palpacion),
        ("Hepatomegalia", examen.abd_hepatomegalia),
        ("Puño", examen.abd_puno),
        ("Hernia Umbilical", examen.abd_hernia_umb),
        ("Hernia Inguinal", examen.abd_hernia_ing),
        ("Anillos Dilatados", examen.abd_anillos_dil),
        ("Anillo Derecho", examen.abd_anillo_der),
        ("Anillo Izquierdo", examen.abd_anillo_izq)
    ]
    elements.append(create_section("ABDOMEN", abd_fields, examen.abd_observaciones))

    # INMUNIZACIONES
    elements.append(create_section("INMUNIZACIONES", [
        ("Antitetánica", examen.inmuno_antitetanica),
        ("Antigripal", examen.inmuno_antigripal)
    ], examen.inmuno_otras))
    
    # ODONTOGRAMA
    drawing_odonto, summary_odonto = generar_dibujo_odontograma(getattr(examen, 'odonto_data', ''))
    elements.append(KeepTogether([
        Paragraph("ODONTOGRAMA (FDI)", section_title_style),
        Spacer(1, 4),
        drawing_odonto,
        Spacer(1, 6),
        Paragraph(summary_odonto, normal_style),
        Spacer(1, 6),
        Paragraph(f"<b>Observaciones Odontograma:</b> {examen.odonto_observaciones or 'Sin observaciones.'}", normal_style),
        Spacer(1, 10)
    ]))
    
    # CONCLUSIÓN
    elements.append(KeepTogether([
        Paragraph("CONCLUSIÓN", section_title_style),
        Paragraph(f"{examen.conclusion or 'Sin conclusión registrada.'}", normal_style),
        Spacer(1, 20)
    ]))

    # FIRMA - Examen Clínico firmado exclusivamente por el Director Médico (Dr. Leandro Zárate)
    from apps.informes.models import Profesional
    director = Profesional.objects.filter(apellido__iexact='ZARATE', nombre__icontains='LEANDRO').first()
    if not director:
        director = Profesional.objects.filter(apellido__icontains='ZARATE').first()
    firmante = director or examen.profesional

    firma_elements = []
    if hasattr(firmante, 'firma') and firmante.firma and firmante.firma.imagen_firma:
        img_firma = firmante.firma.imagen_firma.path
        if os.path.exists(img_firma):
            firma_elements.append(Image(img_firma, width=140, height=75))
            
    firma_elements.append(Paragraph(f"<b>Dr. {firmante.nombre.title()} {firmante.apellido.title()}</b>", ParagraphStyle('CenterBold', parent=bold_style, alignment=TA_CENTER)))
    firma_elements.append(Paragraph("<b>Director Médico</b>", ParagraphStyle('CenterRole', parent=normal_style, alignment=TA_CENTER, fontSize=8.5)))
    if firmante.matricula:
        firma_elements.append(Paragraph(f"{firmante.matricula}", ParagraphStyle('CenterMat', parent=normal_style, alignment=TA_CENTER, fontSize=8)))
    if firmante.especialidad:
        firma_elements.append(Paragraph(f"Esp. {firmante.especialidad.nombre.title()}", ParagraphStyle('CenterEsp', parent=normal_style, alignment=TA_CENTER, fontSize=8)))
    firma_elements.append(Paragraph("Firma y Aclaración", ParagraphStyle('CenterNormal', parent=normal_style, alignment=TA_CENTER, fontSize=7.5, textColor=colors.HexColor('#6B7280'))))

    elements.append(KeepTogether([
        Spacer(1, 25),
        Table([[firma_elements]], colWidths=[200], style=[
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ], hAlign='RIGHT')
    ]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

from reportlab.platypus import PageBreak

def _generar_tabla_estudios(normal_style, section_title_style):
    estudios = [
        "CLINICO", "AUDIOMETRIA", "GESTOS REPETITIVOS", "ALCOHOLEMIA EN ALIENTO",
        "ALCOHOLEMIA EN SANGRE", "ANFETAMINAS", "BARBITURICOS", "BETA HCG - CUALITATIVA",
        "CANABINOIDE EN ORINA", "CHAGAS", "COCAINA EN ORINA", "COLESTEROL HDL",
        "COLESTEROL LDL", "COLESTEROL TOTAL", "CREATININA", "ERITROSEDIMENTACION",
        "GLUCEMIA", "GRUPO Y FACTOR", "HEMOGRAMA", "HEPATITIS B - HBS ANTIGENO",
        "HEPATITIS C - HCV", "HEPATOGRAMA", "LSD"
    ]
    rows = []
    for est in estudios:
        rows.append([Paragraph(est, normal_style)])
    
    t = Table(rows, colWidths=[450], style=[
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ])
    return t

def generar_pdf_informe_preocupacional(preocupacional, examen_fisico=None):
    buffer = io.BytesIO()
    
    # Custom PageTemplate for header/footer on every page
    def header_footer(canvas, doc):
        canvas.saveState()
        width, height = A4
        # Header (Logo and "VISIÓN SALUD")
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 30, height - 70, width=130, height=40, preserveAspectRatio=True, mask='auto')
        
        # Footer
        canvas.setFont('Helvetica', 9)
        if hasattr(preocupacional, 'profesional') and preocupacional.profesional:
            prof = str(preocupacional.profesional)
        else:
            prof = "_________________"
            
        fecha = preocupacional.fecha.strftime("%d/%m/%Y") if preocupacional.fecha else "  /  /    "
        canvas.drawString(30, 30, "Firma del Trabajador")
        canvas.drawString(220, 30, f"Firma del Profesional")
        canvas.drawString(420, 30, f"Fecha: {fecha}")
        canvas.restoreState()

    from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
    from apps.pacientes.models import Paciente
    from apps.preocupacional.models import Preocupacional
    doc = BaseDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=80, bottomMargin=60
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 9
    
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#666666'))
    
    section_title_style = ParagraphStyle(
        'SectionTitleStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11,
        textColor=colors.white, backColor=colors.HexColor('#009999'), spaceBefore=10, spaceAfter=10,
        alignment=TA_CENTER, borderPadding=4,
    )
    
    elements = []
    
    # ==== PÁGINA 1: PORTADA ====
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("INFORME", title_style))
    elements.append(Paragraph("PREOCUPACIONAL", title_style))
    elements.append(Spacer(1, 100))
    # You could add address details here matching the screenshot
    elements.append(Paragraph("Zuviría 352 - Salta Capital - Argentina", normal_style))
    elements.append(Paragraph("+54 387 5 512 612", normal_style))
    elements.append(PageBreak())
    
    # ==== Helper for patient/company data ====
    def get_patient_data_table():
        paciente = preocupacional.paciente
        empresa = paciente.empresa
        
        emp_rs = empresa.nombre if empresa else ""
        emp_tel = empresa.telefono if empresa else ""
        emp_cuit = empresa.cuit if empresa else ""
        emp_dom = empresa.direccion if empresa else ""
        
        t_empresa = Table([
            [Paragraph("<b>Razón Social:</b>", normal_style), Paragraph(emp_rs, normal_style), Paragraph("<b>Teléfono:</b>", normal_style), Paragraph(emp_tel, normal_style)],
            [Paragraph("<b>CUIT:</b>", normal_style), Paragraph(emp_cuit, normal_style), Paragraph("<b>Domicilio:</b>", normal_style), Paragraph(emp_dom, normal_style)],
        ], colWidths=[80, 180, 70, 200])
        
        pac_nombre = f"{paciente.apellido}, {paciente.nombres}" if paciente else ""
        pac_cuil = paciente.cuil if (paciente and paciente.cuil) else (paciente.dni if paciente else "")
        pac_fec = paciente.fecha_nacimiento.strftime("%d/%m/%Y") if paciente and hasattr(paciente, 'fecha_nacimiento') and paciente.fecha_nacimiento else ""
        pac_doc = paciente.dni if paciente else ""
        pac_civ = dict(Paciente.ESTADO_CIVIL_CHOICES).get(paciente.estado_civil, "") if paciente and paciente.estado_civil else ""
        pac_sex = dict(Paciente.SEXO_CHOICES).get(paciente.sexo, "") if paciente and paciente.sexo else ""
        pac_tel = paciente.tel_movil if paciente and hasattr(paciente, 'tel_movil') else ""
        pac_dom = paciente.direccion if paciente and hasattr(paciente, 'direccion') else ""
        pac_loc = paciente.localidad if paciente and hasattr(paciente, 'localidad') else ""
        pac_tarea = preocupacional.tarea_propuesta
        pac_nac = paciente.nacionalidad if paciente and hasattr(paciente, 'nacionalidad') else ""
        
        t_trabajador = Table([
            [Paragraph("<b>Apellido y Nombre:</b>", normal_style), Paragraph(pac_nombre, normal_style), Paragraph("<b>CUIL:</b>", normal_style), Paragraph(str(pac_cuil), normal_style)],
            [Paragraph("<b>Fecha Nac.:</b>", normal_style), Paragraph(pac_fec, normal_style), Paragraph("<b>Documento:</b>", normal_style), Paragraph(str(pac_doc), normal_style)],
            [Paragraph("<b>Estado Civil:</b>", normal_style), Paragraph(pac_civ, normal_style), Paragraph("<b>Sexo:</b>", normal_style), Paragraph(pac_sex, normal_style), Paragraph("<b>Tel.:</b>", normal_style), Paragraph(pac_tel, normal_style)],
            [Paragraph("<b>Domicilio:</b>", normal_style), Paragraph(pac_dom, normal_style), Paragraph("<b>Localidad:</b>", normal_style), Paragraph(pac_loc, normal_style)],
            [Paragraph("<b>Tarea Propuesta:</b>", normal_style), Paragraph(pac_tarea, normal_style), Paragraph("<b>Nacionalidad:</b>", normal_style), Paragraph(pac_nac, normal_style)],
        ])
        
        return [
            Paragraph("<b>Empresa</b>", ParagraphStyle('Emp', parent=bold_style, fontSize=11, textColor=colors.HexColor('#004466'), spaceAfter=5)),
            t_empresa,
            Spacer(1, 10),
            Paragraph("<b>Trabajador</b>", ParagraphStyle('Trab', parent=bold_style, fontSize=11, textColor=colors.HexColor('#004466'), spaceAfter=5)),
            t_trabajador,
            Spacer(1, 15)
        ]

    # ==== PÁGINA 2: EXAMEN PREOCUPACIONAL ====
    elements.append(Paragraph("Examen<br/>Preocupacional", section_title_style))
    elements.extend(get_patient_data_table())
    
    elements.append(Paragraph("Resultado del Examen", ParagraphStyle('SubT', parent=section_title_style, backColor=colors.HexColor('#1f497d'))))
    elements.append(_generar_tabla_estudios(normal_style, section_title_style))
    elements.append(PageBreak())
    
    # ==== PÁGINA 3: MÁS ESTUDIOS Y CONCLUSIÓN ====
    estudios2 = [
        "METANFETAMINAS", "ORINA COMPLETA", "PSA - ANTIGENO PROSTATICO", "TRIGLICERIDOS", "UREA",
        "ELECTROCARDIOGRAMA", "ERGOMETRÍA", "RX TÓRAX FRENTE", "RX COLUMNA LUMBOSACRA F Y P",
        "PSICOTECNICO", "ESPIROMETRÍA", "ELECTROENCEFALOGRAMA"
    ]
    rows2 = [[Paragraph(est, normal_style)] for est in estudios2]
    elements.append(Table(rows2, colWidths=[450], style=[
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Conclusión", ParagraphStyle('SubT', parent=section_title_style, textColor=colors.black, backColor=colors.HexColor('#dbeef3'))))
    
    res = dict(Preocupacional.RESULTADO_CHOICES).get(preocupacional.resultado, "")
    elements.append(Paragraph(f"<b>Aptitud:</b> {res}", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Observaciones:</b> {preocupacional.observaciones}", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Fecha Revisión:</b>", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Patologías:</b>", normal_style))
    elements.append(PageBreak())

    # ==== PÁGINA 4: DECLARACIÓN JURADA ====
    elements.append(Paragraph("Declaración Jurada<br/>Preocupacional", section_title_style))
    elements.extend(get_patient_data_table())
    elements.append(Paragraph("Cuestionario", ParagraphStyle('SubT', parent=section_title_style, backColor=colors.HexColor('#1f497d'))))
    
    def row_yesno(label, val):
        return [Paragraph(label, normal_style), "X" if val else "", "X" if not val else ""]
        
    t_style = TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    # A. Hábitos
    elements.append(Paragraph("<b>A. HÁBITOS</b>", ParagraphStyle('H', parent=bold_style, textColor=colors.HexColor('#1f497d'))))
    elements.append(Table([
        ["SI", "NO", "", "SI", "NO", ""],
        ["X" if preocupacional.fuma else "", "X" if not preocupacional.fuma else "", Paragraph(f"¿Fuma? ¿Cuantos por día?: {preocupacional.fuma_cuantos}", normal_style),
         "X" if preocupacional.toma_alcohol else "", "X" if not preocupacional.toma_alcohol else "", Paragraph(f"¿Toma alcohol? ¿Cuanto por día?: {preocupacional.alcohol_cuanto}", normal_style)]
    ], colWidths=[20, 20, 200, 20, 20, 200], style=t_style))
    elements.append(Spacer(1, 10))

    # B. Fam
    elements.append(Paragraph("<b>B. ANTECEDENTES FAMILIARES (PADRE - MADRE)</b>", ParagraphStyle('H', parent=bold_style, textColor=colors.HexColor('#1f497d'))))
    elements.append(Table([
        ["SI", "NO", Paragraph("Hipertensión Arterial:", normal_style), "SI", "NO", Paragraph("Diabetes:", normal_style)],
        ["SI", "NO", Paragraph("Neurológicas:", normal_style), "SI", "NO", Paragraph("Neoplasias:", normal_style)],
        ["", "", Paragraph("Otras:", normal_style), "", "", ""]
    ], colWidths=[20, 20, 200, 20, 20, 200], style=t_style))
    elements.append(Spacer(1, 10))
    
    # C. Personales
    elements.append(Paragraph("<b>C. ANTECEDENTES PERSONALES</b>", ParagraphStyle('H', parent=bold_style, textColor=colors.HexColor('#1f497d'))))
    elements.append(Table([
        ["SI", "NO", Paragraph(f"¿Tuvo que abandonar algún empleo por razones de salud? Causas: {preocupacional.pers_abandono_causas}", normal_style), 
         "SI", "NO", Paragraph(f"¿Recibió indemnización? Causas: {preocupacional.pers_indemnizacion_causas}", normal_style)]
    ], colWidths=[20, 20, 200, 20, 20, 200], style=t_style))
    elements.append(Spacer(1, 10))
    
    # D. Médicos (solo un fragmento para no extender tanto, similar a P4)
    elements.append(Paragraph("<b>D. ANTECEDENTES MÉDICOS</b>", ParagraphStyle('H', parent=bold_style, textColor=colors.HexColor('#1f497d'))))
    elements.append(PageBreak())
    
    # ==== PÁGINA 5: RESTO DE ANTECEDENTES ====
    elements.append(Paragraph("<i>Declaro que la información suministrada es completa y verídica...</i>", normal_style))
    elements.append(PageBreak())

    # ==== PÁGINA: EXAMEN CLÍNICO Y ODONTOGRAMA (Si existe) ====
    if examen_fisico:
        elements.append(Paragraph("Examen Clínico y Odontograma", section_title_style))
        elements.extend(get_patient_data_table())
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#DC5F43'), spaceBefore=5, spaceAfter=15))

        # Medidas / Signos Vitales (Datos Iniciales)
        peso_val = getattr(examen_fisico, 'peso', '') or '—'
        talla_val = getattr(examen_fisico, 'talla', '') or '—'
        ta_val = getattr(examen_fisico, 'tension_arterial', '') or '—'
        sat_val = getattr(examen_fisico, 'sat_oxigeno', '') or '—'
        fc_val = getattr(examen_fisico, 'frecuencia_cardiaca', '') or '—'
        imc_val = getattr(examen_fisico, 'imc', '') or '—'

        datos_medidas_p = [
            [
                Paragraph(f"<b>A. Peso (Kg):</b> {peso_val}", normal_style),
                Paragraph(f"<b>B. Talla (Cm.):</b> {talla_val}", normal_style),
                Paragraph(f"<b>C. Tensión Arterial (TA):</b> {ta_val}", normal_style),
            ],
            [
                Paragraph(f"<b>D. Sat. O2:</b> {sat_val}", normal_style),
                Paragraph(f"<b>E. Frec. Cardíaca:</b> {fc_val}", normal_style),
                Paragraph(f"<b>F. IMC:</b> {imc_val}", normal_style),
            ]
        ]
        t_medidas_p = Table(datos_medidas_p, colWidths=[178, 178, 179], hAlign='LEFT')
        t_medidas_p.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(Paragraph("<b>Datos Iniciales:</b>", ParagraphStyle('SubHP', parent=normal_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1E293B'))))
        elements.append(Spacer(1, 4))
        elements.append(t_medidas_p)
        elements.append(Spacer(1, 10))
        drawing_odonto_p, summary_odonto_p = generar_dibujo_odontograma(getattr(examen_fisico, 'odonto_data', ''))
        elements.append(drawing_odonto_p)
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(summary_odonto_p, normal_style))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>Observaciones Odontograma:</b> {examen_fisico.odonto_observaciones or 'Sin observaciones.'}", normal_style))
        if examen_fisico.conclusion:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<b>Conclusión:</b> {examen_fisico.conclusion}", normal_style))
        elements.append(PageBreak())

    # ==== PÁGINA 6+: INFORMES ADICIONALES ====
    from apps.informes.models import Informe
    if preocupacional.paciente:
        informes = Informe.objects.filter(paciente=preocupacional.paciente, estado='FINALIZADO').order_by('fecha_creacion')
        for informe in informes:
            elements.append(Paragraph("Informe Médico", section_title_style))
            elements.extend(get_patient_data_table())
            elements.append(Spacer(1, 15))
            
            # Profesional details
            prof_text = str(informe.profesional)
            if informe.profesional.especialidad:
                prof_text += f" - Especialidad: {informe.profesional.especialidad.nombre}"
            elements.append(Paragraph(f"<b>Profesional:</b> {prof_text}", normal_style))
            elements.append(Spacer(1, 15))
            
            # Texto
            texto_html = informe.texto_informe.replace('\n', '<br/>') if informe.texto_informe else ''
            elements.append(Paragraph(texto_html, normal_style))
            elements.append(Spacer(1, 40))
            
            # Firma
            firma_elements = []
            if hasattr(informe.profesional, 'firma') and informe.profesional.firma.imagen_firma:
                img_firma = informe.profesional.firma.imagen_firma.path
                if os.path.exists(img_firma):
                    firma_elements.append(Image(img_firma, width=150, height=80))
            
            firma_elements.append(Paragraph(f"<b>{informe.profesional}</b>", ParagraphStyle('CenterBold', parent=bold_style, alignment=TA_CENTER)))
            firma_elements.append(Paragraph("Firma y Aclaración", ParagraphStyle('CenterNormal', parent=normal_style, alignment=TA_CENTER)))
            
            elements.append(KeepTogether([
                Table([[firma_elements]], colWidths=[200], style=[
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
                ], hAlign='RIGHT')
            ]))
            
            elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
