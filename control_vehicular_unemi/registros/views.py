import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accesos.models import Vehiculo, CodigoQR  # Importamos CodigoQR
from .models import RegistroAcceso
from django.utils import timezone  # Importante para comparar las fechas

@login_required(login_url='login')
def validar_acceso(request):
    resultado = None
    if request.method == 'POST':
        # El escáner ahora inserta el TOKEN criptográfico del QR en este campo
        token_qr = request.POST.get('placa') 
        tipo = request.POST.get('tipo')
        
        try:
            # 1. Buscamos el código QR exacto que coincida con el token escaneado
            qr_escaneado = CodigoQR.objects.get(contenido=token_qr, activo=True)
            
            # 2. Verificamos matemáticamente si el código ya caducó
            if qr_escaneado.fecha_expiracion < timezone.now():
                # Inactivamos el código para que no vuelva a ser usado
                qr_escaneado.activo = False
                qr_escaneado.save()
                resultado = "Error: Acceso Denegado. El código QR ha expirado."
            else:
                # 3. Si el código es válido y está en tiempo, registramos el acceso
                vehiculo = qr_escaneado.vehiculo
                RegistroAcceso.objects.create(vehiculo=vehiculo, tipo=tipo)
                resultado = f"Acceso de {tipo} registrado exitosamente para: {vehiculo.marca} - {vehiculo.placa}"
                
        except CodigoQR.DoesNotExist:
            resultado = "Error: Código QR inválido, inactivo o no autorizado."
            
    return render(request, 'registros/validar.html', {'resultado': resultado})

@login_required(login_url='login')
def dashboard_guardia(request):
    # ... (Mantén tu código actual del dashboard_guardia intacto aquí) ...
    ultimos_accesos = RegistroAcceso.objects.select_related('vehiculo').order_by('-fecha_hora')[:10]
    total_entradas = RegistroAcceso.objects.filter(tipo='Entrada').count()
    total_salidas = RegistroAcceso.objects.filter(tipo='Salida').count()
    vehiculos_dentro = max(0, total_entradas - total_salidas)
    
    context = {
        'ultimos_accesos': ultimos_accesos,
        'vehiculos_dentro': vehiculos_dentro,
    }
    return render(request, 'registros/dashboard.html', context)

@login_required(login_url='login')
def exportar_reporte_csv(request):
    # Preparamos el archivo para que el navegador lo descargue
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_accesos_unemi.csv"'
    
    # Creamos el "escritor" del archivo
    writer = csv.writer(response)
    
    # Escribimos los encabezados de las columnas
    writer.writerow(['Placa', 'Marca', 'Propietario', 'Tipo de Evento', 'Fecha y Hora'])
    
    # Traemos todos los registros de la base de datos
    accesos = RegistroAcceso.objects.select_related('vehiculo', 'vehiculo__propietario').all().order_by('-fecha_hora')
    
    # Llenamos el archivo fila por fila
    for acceso in accesos:
        fecha_formateada = acceso.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        nombre_propietario = acceso.vehiculo.propietario.nombre if acceso.vehiculo.propietario else "Sin registro"
        
        writer.writerow([
            acceso.vehiculo.placa,
            acceso.vehiculo.marca,
            nombre_propietario,
            acceso.tipo,
            fecha_formateada
        ])
        
    return response