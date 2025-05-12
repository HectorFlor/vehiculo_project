
from django.urls import path
from . import views

app_name = 'vehiculos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('solicitar/', views.solicitar_vehiculo, name='solicitar_vehiculo'),
    path('solicitudes/mis-aprobadas/', views.solicitudes_aprobadas_chofer, name='mis_solicitudes_aprobadas'),
    path('solicitudes/pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('solicitudes/<int:solicitud_id>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitudes/<int:solicitud_id>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('checklist/<int:solicitud_id>/salida/', views.completar_checklist_salida, name='completar_checklist_salida'),
    path('verificar-checklists/', views.verificar_checklist_guardia, name='verificar_checklist'),
    path('confirmar-checklist/<int:checklist_id>/', views.confirmar_checklist, name='confirmar_checklist'),
    path('checklist/<int:solicitud_id>/retorno/', views.completar_checklist_retorno, name='completar_checklist_retorno'),
    path('verificar-checklists-retorno/', views.verificar_checklist_retorno_guardia, name='verificar_checklist_retorno'),
    path('confirmar-checklist-retorno/<int:checklist_id>/', views.confirmar_checklist_retorno, name='confirmar_checklist_retorno'),
    
]
