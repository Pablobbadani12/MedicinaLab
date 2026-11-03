from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.core.exceptions import ValidationError


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
