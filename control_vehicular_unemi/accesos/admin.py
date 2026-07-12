from django.contrib import admin
from .models import Propietario, Vehiculo, ConfiguracionQR, CodigoQR

# Registramos los modelos básicos
admin.site.register(Propietario)
admin.site.register(Vehiculo)

# Registramos la configuración para que puedas definir el tiempo de renovación
@admin.register(ConfiguracionQR)
class ConfiguracionQRAdmin(admin.ModelAdmin):
    list_display = ('administrador', 'tiempo_renovacion', 'unidad_tiempo', 'fecha_modificacion')

@admin.register(CodigoQR)
class CodigoQRAdmin(admin.ModelAdmin):
    # Añadimos 'contenido' a esta línea:
    list_display = ('vehiculo', 'contenido', 'fecha_creacion', 'fecha_expiracion', 'activo')
    search_fields = ('vehiculo__placa',)