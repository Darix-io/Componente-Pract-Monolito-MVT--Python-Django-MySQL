from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
import uuid

class Propietario(models.Model):
    id_propietario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    numero_identidad = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class ConfiguracionQR(models.Model):
    id_configuracion_qr = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tiempo_renovacion = models.IntegerField()  
    unidad_tiempo = models.CharField(max_length=20, default='minutos')  
    fecha_modificacion = models.DateField(auto_now=True)

    def __str__(self):
        return f"Configuración: {self.tiempo_renovacion} {self.unidad_tiempo}"

class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    estado = models.CharField(max_length=50, default='Autorizado')

    def __str__(self):
        return f"{self.marca} - {self.placa}"

    def generar_nuevo_qr(self):
        # 1. Invalidar todos los QRs anteriores de este vehículo
        CodigoQR.objects.filter(vehiculo=self, activo=True).update(activo=False)
        
        # 2. Obtener la última configuración del administrador
        config = ConfiguracionQR.objects.last()
        if not config:
            print("¡ALERTA DEBUG!: No se encontró ninguna Configuración QR en la base de datos.")
            return None
            
        # 3. Calcular fecha y hora de expiración exacta
        ahora = timezone.now()
        if config.unidad_tiempo == 'minutos':
            expiracion = ahora + timedelta(minutes=config.tiempo_renovacion)
        elif config.unidad_tiempo == 'horas':
            expiracion = ahora + timedelta(hours=config.tiempo_renovacion)
        else:
            expiracion = ahora + timedelta(days=config.tiempo_renovacion)
            
        # 4. Generar token criptográfico único 
        token = str(uuid.uuid4())
        
        # 5. Crear el archivo visual del QR
        qr = qrcode.make(token)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        
        # 6. Guardar en base de datos
        nuevo_qr = CodigoQR(
            vehiculo=self,
            contenido=token,
            fecha_expiracion=expiracion,
            activo=True
        )
        nuevo_qr.imagen.save(f"qr_{self.placa}_{token[:8]}.png", ContentFile(buffer.getvalue()), save=False)
        nuevo_qr.save()
        print(f"¡ÉXITO DEBUG!: Se generó un nuevo QR para {self.placa} con Token: {token}")
        return nuevo_qr

    def save(self, *args, **kwargs):
        # Primero guardamos el vehículo
        super().save(*args, **kwargs)
        # Luego, si no tiene un código QR activo, le generamos uno automáticamente
        if not CodigoQR.objects.filter(vehiculo=self, activo=True).exists():
            self.generar_nuevo_qr()


class CodigoQR(models.Model):
    id_codigo_qr = models.AutoField(primary_key=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    contenido = models.TextField()  
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='qrs_dinamicos/', blank=True)

    def __str__(self):
        return f"QR {self.vehiculo.placa} - {'Activo' if self.activo else 'Inactivo'}"