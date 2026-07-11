from django.contrib import admin
from .models import RegistroAcceso

@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'tipo', 'fecha_hora')
    list_filter = ('tipo', 'fecha_hora')