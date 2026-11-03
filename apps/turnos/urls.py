from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('', views.reserva_turno_list, name='reserva_list'),
]
