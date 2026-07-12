from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Rutas de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registros/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Rutas operativas
    path('validar/', views.validar_acceso, name='validar_acceso'),
    path('dashboard/', views.dashboard_guardia, name='dashboard_guardia'),
    
    # ¡ESTA ES LA LÍNEA QUE LE FALTABA AL BOTÓN!
    path('exportar/', views.exportar_reporte_csv, name='exportar_reporte'),
]