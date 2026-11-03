from django.urls import path
from . import views

app_name = 'informes'
urlpatterns = [
    path('', views.informe_list, name='informe_list'),
    path('nuevo/', views.informe_create, name='informe_create'),
    path('<int:pk>/', views.informe_detail, name='informe_detail'),
    path('<int:pk>/editar/', views.informe_edit, name='informe_edit'),
    path('<int:pk>/eliminar/', views.informe_delete, name='informe_delete'),
    path('<int:pk>/imprimir/', views.imprimir_informe, name='imprimir_informe'),
    path('<int:pk>/verificar-firma/', views.verificar_firma, name='verificar_firma'),
    path('paciente/<int:pk_paciente>/consolidado/', views.imprimir_consolidado, name='imprimir_consolidado'),
]
