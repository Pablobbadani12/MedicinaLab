from django.db import models
from apps.empresas.models import Empresa


class Paciente(models.Model):

    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'),
        ('C', 'Casado/a'),
        ('D', 'Divorciado/a'),
        ('V', 'Viudo/a'),
    ]

    SEXO_CHOICES = [
        ('M', 'Varón'),
        ('F', 'Mujer'),
        ('X', 'Sin Especificar'),
    ]

    apellido        = models.CharField(max_length=200, verbose_name='Apellido')
    nombres         = models.CharField(max_length=200, verbose_name='Nombres')
    dni             = models.CharField(max_length=30, unique=True, verbose_name='DNI / Pasaporte')
    cuil            = models.CharField(max_length=11, blank=True, verbose_name='CUIL')
    direccion       = models.CharField(max_length=300, blank=True, verbose_name='Dirección')
    tel_movil       = models.CharField(max_length=50, blank=True, verbose_name='Tel. Móvil')
    email           = models.EmailField(max_length=200, blank=True, verbose_name='Email')
    empresa         = models.ForeignKey(
                        Empresa,
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        verbose_name='Empresa',
                        related_name='pacientes',
                      )
    estado_civil    = models.CharField(
                        max_length=1,
                        choices=ESTADO_CIVIL_CHOICES,
                        blank=True,
                        verbose_name='Estado Civil',
                      )
    sexo            = models.CharField(
                        max_length=1,
                        choices=SEXO_CHOICES,
                        blank=True,
                        verbose_name='Sexo',
                      )
    nacionalidad    = models.CharField(max_length=100, blank=True, verbose_name='Nacionalidad')
    tarea_propuesta = models.TextField(max_length=500, blank=True, verbose_name='Tarea Propuesta')
    fecha_nacimiento= models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    localidad       = models.CharField(max_length=100, blank=True, verbose_name='Localidad')

    class Meta:
        db_table = 'ml_paciente'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombres']

    def __str__(self):
        return f"{self.apellido}, {self.nombres}"

    def nombre_completo(self):
        return f"{self.apellido}, {self.nombres}"

    # ── Propiedades de compatibilidad (usadas por services.py / PDFs) ──
    @property
    def nro_doc(self):
        return self.dni

    @property
    def telcelu(self):
        return self.tel_movil

    @property
    def telfijo(self):
        return ''

    @property
    def domicilio(self):
        return self.direccion

    @property
    def fecnaci(self):
        return self.fecha_nacimiento

    @property
    def genero(self):
        return self.get_sexo_display() if self.sexo else ''
