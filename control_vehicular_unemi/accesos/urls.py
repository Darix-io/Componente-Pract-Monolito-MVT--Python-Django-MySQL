from django.urls import path
from . import views

urlpatterns = [
    path('vehiculos/', views.listar_vehiculos, name='listar_vehiculos'),
]