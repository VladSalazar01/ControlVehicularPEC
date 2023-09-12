from django.urls import path
from . import views
from .views import *


urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('iniciar_sesion/', views.user_login, name='iniciar_sesion'),
    
    #partes policiales consultar
    path('mis_partes_policiales/', mis_partes_policiales, name='mis_partes_policiales'),
    #nuevo partes poiliciales
    #agregar
    path('mantenimiento/', PartePolicialCreateView.as_view(), name='mantenimiento'),    
    #pdf
    path('parte_policial_pdf/<int:parte_id>/', parte_policial_pdf, name='parte_policial_pdf'),

    #orden de trabajo
    #pdf
    path('orden_mantenimiento_pdf/<int:orden_mantenimiento_id>/', orden_mantenimiento_pdf, name='orden_mantenimiento_pdf'),
    path('finalizar_orden_mantenimiento/<int:orden_mantenimiento_id>/', views.finalizar_orden_mantenimiento, name='finalizar_orden'),

    #evaluacion buzon de quejas
    path('queja_sugerencia/', views.queja_sugerencia, name='queja_sugerencia'),
    path('get_subcircuitos/<int:circuito_id>/', views.get_subcircuitos, name='get_subcircuitos'),
    path('admin/reporte_quejas_sugerencias/', views.reporte_quejas_sugerencias, name='reporte_quejas_sugerencias'),
    path('admin/reporte_quejas_sugerencias_pdf/', views.reporte_quejas_sugerencias_pdf, name='reporte_quejas_sugerencias_pdf'),
    
]
