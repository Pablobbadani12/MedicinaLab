import os
from urllib.parse import quote
from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'ml_especialidad'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return self.nombre

class Profesional(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'ml_profesional'
        verbose_name = 'Profesional'
        verbose_name_plural = 'Profesionales'

    def __str__(self):
        return f"Dr/a. {self.apellido}, {self.nombre}"

class UsuarioSistema(models.Model):
    username = models.CharField(max_length=150, unique=True)
    nombre_completo = models.CharField(max_length=200)

    class Meta:
        db_table = 'ml_usuario'
        verbose_name = 'Usuario Sistema'
        verbose_name_plural = 'Usuarios Sistema'

class FirmaDigital(models.Model):
    profesional = models.OneToOneField(Profesional, on_delete=models.CASCADE, related_name='firma')
    imagen_firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    hash_firma = models.CharField(max_length=255, blank=True, help_text="Hash criptográfico si aplica")

    class Meta:
        db_table = 'ml_firmadigi'
        verbose_name = 'Firma Digital'
        verbose_name_plural = 'Firmas Digitales'

class Informe(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EN_REVISION', 'En Revisión'),
        ('FINALIZADO', 'Finalizado'),
    ]
    turno = models.ForeignKey(
        'turnos.ReservaTurno',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='informes',
        verbose_name='Turno de origen',
    )
    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='informes',
        verbose_name='Paciente',
        db_column='PACIENTE_ID',
    )
    profesional = models.ForeignKey(Profesional, on_delete=models.PROTECT, related_name='informes_realizados')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='informes_empresa')
    texto_informe = models.TextField(max_length=1024, validators=[MaxLengthValidator(1024)], help_text="Máximo 1024 caracteres.")
    archivo_pdf = models.FileField(upload_to='informes_pdf/%Y/%m/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])], help_text="Subir documento PDF o imagen (JPG, PNG).", blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR')
    firma_timestamp = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora en que se firmó digitalmente el informe")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ml_informe'
        verbose_name = 'Informe Médico'
        verbose_name_plural = 'Informes Médicos'
        ordering = ['-fecha_creacion']

    def clean(self):
        if self.pk:
            old_instance = Informe.objects.get(pk=self.pk)
            if old_instance.estado == 'FINALIZADO':
                raise ValidationError("No se puede modificar un informe que ya está FINALIZADO.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        paciente_str = str(self.paciente) if self.paciente else '(sin paciente)'
        return f"Informe {self.id} - {paciente_str}"

    # ── Gestión de múltiples archivos adjuntos (PDF / Imágenes) ──────────────
    def _extra_adjuntos_dir(self):
        if not self.pk:
            return None
        return os.path.join(settings.MEDIA_ROOT, 'informes_pdf', 'extra', str(self.pk))

    @staticmethod
    def _clean_display_name(filename):
        base = os.path.basename(filename)
        if '__' in base and base.split('__', 1)[0].isdigit():
            return base.split('__', 1)[1]
        return base

    @property
    def archivos_adjuntos(self):
        """
        Retorna la lista ordenada de todos los archivos adjuntos del informe:
        [{'key': ..., 'name': ..., 'url': ..., 'path': ...}, ...]
        """
        items = []
        main_abspath = None
        if self.archivo_pdf and self.archivo_pdf.name:
            try:
                main_path = self.archivo_pdf.path
                main_abspath = os.path.abspath(main_path)
                if os.path.exists(main_path):
                    items.append({
                        'key': 'main',
                        'name': self._clean_display_name(self.archivo_pdf.name),
                        'url': self.archivo_pdf.url,
                        'path': main_path,
                    })
            except Exception:
                pass

        extra_dir = self._extra_adjuntos_dir()
        if extra_dir and os.path.isdir(extra_dir):
            for fname in sorted(os.listdir(extra_dir)):
                fpath = os.path.join(extra_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                if main_abspath and os.path.abspath(fpath) == main_abspath:
                    continue
                rel_url = f"{settings.MEDIA_URL.rstrip('/')}/informes_pdf/extra/{self.pk}/{quote(fname)}"
                items.append({
                    'key': f"extra:{fname}",
                    'name': self._clean_display_name(fname),
                    'url': rel_url,
                    'path': fpath,
                })
        return items

    @property
    def tiene_archivos_adjuntos(self):
        return len(self.archivos_adjuntos) > 0

    def eliminar_archivos_adjuntos(self, keys_to_delete):
        """Elimina los adjuntos indicados por su 'key' y reasigna archivo_pdf si corresponde."""
        if not keys_to_delete or not self.pk:
            return
        keys_set = set(keys_to_delete)
        extra_dir = self._extra_adjuntos_dir()

        # 1. Eliminar archivos extra seleccionados
        if extra_dir and os.path.isdir(extra_dir):
            for key in keys_set:
                if key.startswith('extra:'):
                    fname = os.path.basename(key.split(':', 1)[1])
                    fpath = os.path.join(extra_dir, fname)
                    if os.path.isfile(fpath):
                        try:
                            os.remove(fpath)
                        except OSError:
                            pass

        # 2. Si se pidió eliminar el archivo principal ('main')
        if 'main' in keys_set and self.archivo_pdf and self.archivo_pdf.name:
            try:
                old_path = self.archivo_pdf.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            except Exception:
                pass

            # Promover el siguiente archivo extra (si queda alguno) como archivo_pdf principal
            promoted = False
            if extra_dir and os.path.isdir(extra_dir):
                remaining = [
                    f for f in sorted(os.listdir(extra_dir))
                    if os.path.isfile(os.path.join(extra_dir, f))
                ]
                if remaining:
                    next_fname = remaining[0]
                    self.archivo_pdf.name = f"informes_pdf/extra/{self.pk}/{next_fname}"
                    Informe.objects.filter(pk=self.pk).update(archivo_pdf=self.archivo_pdf.name)
                    promoted = True

            if not promoted:
                self.archivo_pdf = None
                Informe.objects.filter(pk=self.pk).update(archivo_pdf='')

    def agregar_archivos_adjuntos(self, uploaded_files):
        """
        Guarda uno o más archivos adjuntos en el informe.
        Si no tiene archivo_pdf principal aún, el primero se guarda en archivo_pdf
        y los siguientes en media/informes_pdf/extra/<id>/.
        """
        if not uploaded_files or not self.pk:
            return

        files_list = list(uploaded_files)
        # Verificar si ya existe un archivo principal válido en disco
        has_main = False
        if self.archivo_pdf and self.archivo_pdf.name:
            try:
                has_main = os.path.isfile(self.archivo_pdf.path)
            except Exception:
                has_main = False

        if not has_main and files_list:
            first_file = files_list.pop(0)
            self.archivo_pdf.save(first_file.name, first_file, save=False)
            Informe.objects.filter(pk=self.pk).update(archivo_pdf=self.archivo_pdf.name)

        if files_list:
            extra_dir = self._extra_adjuntos_dir()
            os.makedirs(extra_dir, exist_ok=True)
            existing_indices = []
            for fname in os.listdir(extra_dir):
                if '__' in fname and fname.split('__', 1)[0].isdigit():
                    existing_indices.append(int(fname.split('__', 1)[0]))
            next_idx = (max(existing_indices) + 1) if existing_indices else 1

            for f in files_list:
                safe_name = get_valid_filename(os.path.basename(f.name)) or 'adjunto.pdf'
                stored_name = f"{next_idx:03d}__{safe_name}"
                next_idx += 1
                dest_path = os.path.join(extra_dir, stored_name)
                with open(dest_path, 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)


class PerfilProfesional(models.Model):
    """
    Vincula un User de Django con un Profesional del sistema.
    Se usa cuando el usuario pertenece al grupo PRESTADORES.
    Ambos modelos viven en Oracle, por lo que la relación es un FK real.
    """
    profesional = models.OneToOneField(
        Profesional,
        on_delete=models.CASCADE,
        related_name='perfil_usuario',
        verbose_name='Profesional',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_profesional',
        verbose_name='Usuario',
    )

    class Meta:
        db_table = 'ml_perfil_profesional'
        verbose_name = 'Perfil de Profesional'
        verbose_name_plural = 'Perfiles de Profesionales'

    def __str__(self):
        return f"{self.profesional} → {self.user.username}"
