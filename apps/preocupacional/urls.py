from django.urls import path
from . import views

app_name = 'preocupacional'

urlpatterns = [
    path('', views.preocupacional_list, name='preocupacional_list'),
    path('nuevo/<int:pk_paciente>/', views.preocupacional_create, name='preocupacional_create'),
    path('<int:pk>/editar/', views.preocupacional_edit, name='preocupacional_edit'),
    path('<int:pk>/pdf/', views.preocupacional_pdf, name='preocupacional_pdf'),
    path('examen-clinico/', views.examen_fisico_list, name='examen_fisico_list'),
    path('examen-clinico/turno/<int:turno_id>/', views.examen_fisico_form_view, name='examen_fisico_form'),
    path('examen-clinico/<int:pk>/pdf/', views.examen_fisico_pdf, name='examen_fisico_pdf'),
]
