from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # <-- Agrega esta línea
from accesos.models import Vehiculo
from .models import RegistroAcceso, TipoAcceso

@login_required(login_url='/admin/login/')
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

@login_required(login_url='/admin/login/')
def dashboard_guardia(request):
    # Obtener los últimos 10 accesos registrados en el sistema
    ultimos_accesos = RegistroAcceso.objects.select_related('vehiculo').order_by('-fecha_hora')[:10]
    
    # Cálculo rápido para el contador del campus
    total_entradas = RegistroAcceso.objects.filter(tipo='Entrada').count()
    total_salidas = RegistroAcceso.objects.filter(tipo='Salida').count()
    vehiculos_dentro = max(0, total_entradas - total_salidas)
    
    context = {
        'ultimos_accesos': ultimos_accesos,
        'vehiculos_dentro': vehiculos_dentro,
    }
    return render(request, 'registros/dashboard.html', context)