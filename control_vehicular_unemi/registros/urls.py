from django.urls import path
from . import views

urlpatterns = [
    path('validar/', views.validar_acceso, name='validar_acceso'),
    path('dashboard/', views.dashboard_guardia, name='dashboard_guardia'), # <--- Agrega esta línea
]