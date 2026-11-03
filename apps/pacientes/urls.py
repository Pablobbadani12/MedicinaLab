from django.urls import path
from . import views

app_name = 'pacientes'
urlpatterns = [
    path('', views.paciente_list, name='paciente_list'),
    path('nuevo/', views.paciente_create, name='paciente_create'),
    path('buscar-json/', views.paciente_search_json, name='paciente_search_json'),
    path('<int:pk>/', views.paciente_detail, name='paciente_detail'),
    path('<int:pk>/editar/', views.paciente_edit, name='paciente_edit'),
    path('<int:pk>/eliminar/', views.paciente_delete, name='paciente_delete'),
]
