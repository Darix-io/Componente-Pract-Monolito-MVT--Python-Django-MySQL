from django.shortcuts import render, redirect
from accesos.models import Vehiculo
from .models import RegistroAcceso, TipoAcceso

def validar_acceso(request):
    resultado = None
    if request.method == 'POST':
        placa = request.POST.get('placa')
        tipo = request.POST.get('tipo')
        try:
            vehiculo = Vehiculo.objects.get(placa=placa)
            # Creamos el registro en la bitácora
            RegistroAcceso.objects.create(vehiculo=vehiculo, tipo=tipo)
            resultado = f"Acceso de {tipo} registrado exitosamente para: {vehiculo.marca} - {vehiculo.placa}"
        except Vehiculo.DoesNotExist:
            resultado = "Error: Vehículo no encontrado en la base de datos."
            
    return render(request, 'registros/validar.html', {'resultado': resultado})