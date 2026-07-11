import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models

class Propietario(models.Model):
    id_propietario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    numero_identidad = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    id_propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.placa} - {self.marca}"
    
    qr_code = models.ImageField(upload_to='qrs/', blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            # Creamos el QR con la placa como identificador único
            qr = qrcode.make(self.placa)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            self.qr_code.save(f"{self.placa}.png", ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)