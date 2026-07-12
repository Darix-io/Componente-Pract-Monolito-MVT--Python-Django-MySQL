import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accesos.models import Vehiculo, CodigoQR
from .models import RegistroAcceso
from django.utils import timezone

@login_required(login_url='login')
def validar_acceso(request):
    if request.method == 'POST':
        token_qr = request.POST.get('placa') 
        tipo = request.POST.get('tipo')
        
        try:
            qr_escaneado = CodigoQR.objects.get(contenido=token_qr, activo=True)
            
            if qr_escaneado.fecha_expiracion < timezone.now():
                qr_escaneado.activo = False
                qr_escaneado.save()
                return render(request, 'registros/validar_acceso.html', {
                    'es_valido': False, 'mensaje': "El código QR ha expirado."
                })
            else:
                vehiculo = qr_escaneado.vehiculo
                RegistroAcceso.objects.create(vehiculo=vehiculo, tipo=tipo)
                return render(request, 'registros/validar_acceso.html', {
                    'es_valido': True, 'vehiculo': vehiculo
                })
                
        except CodigoQR.DoesNotExist:
            return render(request, 'registros/validar_acceso.html', {
                'es_valido': False, 'mensaje': "Código inválido o no autorizado."
            })
            
    return render(request, 'registros/validar.html')

@login_required(login_url='login')
def dashboard_guardia(request):
    ultimos_accesos = RegistroAcceso.objects.select_related('vehiculo').order_by('-fecha_hora')[:10]
    total_entradas = RegistroAcceso.objects.filter(tipo='Entrada').count()
    total_salidas = RegistroAcceso.objects.filter(tipo='Salida').count()
    vehiculos_dentro = max(0, total_entradas - total_salidas)
    return render(request, 'registros/dashboard.html', {
        'ultimos_accesos': ultimos_accesos, 'vehiculos_dentro': vehiculos_dentro
    })

@login_required(login_url='login')
def exportar_reporte_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_accesos_unemi.csv"'
    writer = csv.writer(response)
    writer.writerow(['Placa', 'Marca', 'Propietario', 'Tipo de Evento', 'Fecha y Hora'])
    accesos = RegistroAcceso.objects.select_related('vehiculo', 'vehiculo__propietario').all().order_by('-fecha_hora')
    for acceso in accesos:
        fecha_formateada = acceso.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        nombre_propietario = acceso.vehiculo.propietario.nombre if acceso.vehiculo.propietario else "Sin registro"
        writer.writerow([acceso.vehiculo.placa, acceso.vehiculo.marca, nombre_propietario, acceso.tipo, fecha_formateada])
    return response