from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import os


# ─────────────────────────────────────────────────────────────────────────────
# Helper: dibuja texto con wrap automático y devuelve la nueva posición Y
# ─────────────────────────────────────────────────────────────────────────────
def _draw_wrapped(c, text, x, y, max_width, font, size, leading=14):
    c.setFont(font, size)
    lines = simpleSplit(text, font, size, max_width)
    for line in lines:
        if y < 60:
            c.showPage()
            y = letter[1] - 60
            c.setFont(font, size)
        c.drawString(x, y, line)
        y -= leading
    return y


# ─────────────────────────────────────────────────────────────────────────────
# PDF individual de un único informe
# ─────────────────────────────────────────────────────────────────────────────
def generar_pdf_informe(informe):
    """Genera el PDF de un informe individual y, si tiene adjunto PDF, lo anexa al final."""
    from pypdf import PdfWriter, PdfReader
    from django.conf import settings
    from datetime import date

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 45
    content_width = width - margin * 2

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        # Escalar logo razonablemente
        c.drawImage(logo_path, margin, height - 90, width=180, height=60, preserveAspectRatio=True, mask='auto')

    # Línea horizontal
    y = height - 105
    c.setStrokeColorRGB(0.86, 0.40, 0.28) # Naranja/rojo de Visión Salud
    c.setLineWidth(1.5)
    c.line(margin, y, width - margin, y)

    y -= 35

    paciente = informe.paciente
    nombre = f"{paciente.nombres or ''} {paciente.apellido or ''}".strip() if paciente else "—"
    
    edad = "—"
    if paciente and paciente.fecnaci:
        today = date.today()
        edad_num = today.year - paciente.fecnaci.year - ((today.month, today.day) < (paciente.fecnaci.month, paciente.fecnaci.day))
        edad = str(edad_num)

    dni = paciente.dni if paciente else "—"
    fecha = informe.fecha_creacion.strftime("%d/%m/%Y") if informe.fecha_creacion else "—"

    # Datos
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    
    col1 = margin
    col2 = margin + 120

    c.drawString(col1, y, "Nombre y Apellido:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, nombre)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Edad:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, edad)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "DNI:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, dni)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Fecha:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, fecha)
    y -= 45
    
    # Informe
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Informe:")
    
    c.setFont("Helvetica", 10)
    texto = informe.texto_informe or ""
    lines = simpleSplit(texto, "Helvetica", 10, content_width - 80)
    
    x_text = col1 + 80
    
    for line in lines:
        if y < 60:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 10)
        c.drawString(x_text, y, line)
        y -= 14

    c.save()
    buffer.seek(0)
    informe_pdf_bytes = buffer.getvalue()

    # ── Combinar con PDF adjunto si existe ───────────────────────────────────
    if informe.archivo_pdf and os.path.exists(informe.archivo_pdf.path):
        writer = PdfWriter()

        # Páginas del informe generado
        reader_informe = PdfReader(BytesIO(informe_pdf_bytes))
        for page in reader_informe.pages:
            writer.add_page(page)

        ext = os.path.splitext(informe.archivo_pdf.path)[1].lower()
        try:
            if ext in ('.jpg', '.jpeg', '.png'):
                from PIL import Image as PilImage
                from reportlab.lib.pagesizes import letter as letter_size

                img = PilImage.open(informe.archivo_pdf.path).convert('RGB')
                img_width, img_height = img.size
                page_w, page_h = letter_size

                scale = min(page_w / img_width, page_h / img_height)
                draw_w = img_width * scale
                draw_h = img_height * scale
                x_off = (page_w - draw_w) / 2
                y_off = (page_h - draw_h) / 2

                img_buffer = BytesIO()
                img_c = canvas.Canvas(img_buffer, pagesize=letter_size)
                img_c.drawInlineImage(img, x_off, y_off, draw_w, draw_h)
                img_c.save()
                img_buffer.seek(0)

                reader_adjunto = PdfReader(img_buffer)
            else:
                reader_adjunto = PdfReader(informe.archivo_pdf.path)

            for page in reader_adjunto.pages:
                writer.add_page(page)
        except Exception:
            pass 

        out = BytesIO()
        writer.write(out)
        out.seek(0)
        return out.getvalue()

    return informe_pdf_bytes


# ─────────────────────────────────────────────────────────────────────────────
# PDF consolidado (historial completo del paciente — existente)
# ─────────────────────────────────────────────────────────────────────────────
def generar_pdf_consolidado(paciente, informes):
    from django.conf import settings
    from datetime import date

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 45
    content_width = width - margin * 2

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, margin, height - 90, width=180, height=60, preserveAspectRatio=True, mask='auto')

    # Línea horizontal
    y = height - 105
    c.setStrokeColorRGB(0.86, 0.40, 0.28) 
    c.setLineWidth(1.5)
    c.line(margin, y, width - margin, y)

    y -= 35

    nombre = f"{paciente.nombres or ''} {paciente.apellido or ''}".strip() if paciente else "—"
    
    edad = "—"
    if paciente and paciente.fecnaci:
        today = date.today()
        edad_num = today.year - paciente.fecnaci.year - ((today.month, today.day) < (paciente.fecnaci.month, paciente.fecnaci.day))
        edad = str(edad_num)

    dni = paciente.dni if paciente else "—"
    fecha = date.today().strftime("%d/%m/%Y")

    # Datos
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    
    col1 = margin
    col2 = margin + 120

    c.drawString(col1, y, "Nombre y Apellido:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, nombre)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Edad:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, edad)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "DNI:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, dni)
    y -= 25
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Fecha:")
    c.setFont("Helvetica", 11)
    c.drawString(col2, y, fecha)
    y -= 45

    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1, y, "Informe:")
    
    c.setFont("Helvetica", 10)
    x_text = col1 + 80
    
    for inf in informes:
        texto = f"--- Informe #{inf.id} ({inf.fecha_creacion.strftime('%d/%m/%Y')}) ---\n"
        texto += inf.texto_informe or ""
        lines = simpleSplit(texto, "Helvetica", 10, content_width - 80)
        
        for line in lines:
            if y < 60:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(x_text, y, line)
            y -= 14
        y -= 14

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
