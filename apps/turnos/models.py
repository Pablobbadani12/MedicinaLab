from django.db import models
from apps.pacientes.models import Paciente
from apps.informes.models import Profesional


class ReservaTurno(models.Model):

    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('PRESENTE',    'Presente'),
        ('FINALIZADO',  'Finalizado'),
    ]

    paciente    = models.ForeignKey(
                    Paciente,
                    on_delete=models.PROTECT,
                    verbose_name='Paciente',
                    related_name='turnos',
                  )
    profesional = models.ForeignKey(
                    Profesional,
                    on_delete=models.PROTECT,
                    verbose_name='Profesional',
                    related_name='turnos',
                  )
    fecha_visita = models.DateField(verbose_name='Fecha de visita')
    hora_visita  = models.TimeField(verbose_name='Hora de visita')
    estado       = models.CharField(
                    max_length=12,
                    choices=ESTADO_CHOICES,
                    default='PENDIENTE',
                    verbose_name='Estado',
                  )
    observaciones = models.TextField(
                    blank=True,
                    verbose_name='Observaciones',
                    help_text='Notas adicionales sobre el turno (opcional).',
                  )
    fecha_creacion      = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        db_table         = 'ml_reserva_turno'
        verbose_name     = 'Reserva de Turno'
        verbose_name_plural = 'Reservas de Turno'
        ordering         = ['fecha_visita', 'hora_visita']

    def __str__(self):
        return (
            f"{self.paciente} — "
            f"{self.fecha_visita.strftime('%d/%m/%Y')} {self.hora_visita.strftime('%H:%M')} — "
            f"{self.profesional}"
        )
