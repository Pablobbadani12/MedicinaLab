from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    cuit = models.CharField(max_length=13, unique=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'ml_empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre
