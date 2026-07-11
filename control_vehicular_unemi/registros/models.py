from django.db import models
from accesos.models import Vehiculo

class TipoAcceso(models.TextChoices):
    ENTRADA = 'Entrada', 'Entrada'
    SALIDA = 'Salida', 'Salida'

class RegistroAcceso(models.Model):
    id_registro = models.AutoField(primary_key=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TipoAcceso.choices)

    def __str__(self):
        return f"{self.vehiculo.placa} - {self.tipo} - {self.fecha_hora}"