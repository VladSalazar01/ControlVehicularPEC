from django.urls import path
from . import views
from .views import *


urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('iniciar_sesion/', views.user_login, name='iniciar_sesion'),
    #partes policiales crear
    path('parte_policial/', parte_policial, name='parte_policial'),
    path('status/<str:status>/', status, name='status'),

    
    #partes policiales consultar
    path('mis_partes_policiales/', mis_partes_policiales, name='mis_partes_policiales'),

    #nuevo partes poilicles
    #agregar
    path('mantenimiento/', PartePolicialCreateView.as_view(), name='mantenimiento'),


    #evaluacion buzon de quejas
    path('queja_sugerencia/', views.queja_sugerencia, name='queja_sugerencia'),
    path('get_subcircuitos/<int:circuito_id>/', views.get_subcircuitos, name='get_subcircuitos'),
    path('admin/reporte_quejas_sugerencias/', views.reporte_quejas_sugerencias, name='reporte_quejas_sugerencias'),
    path('admin/reporte_quejas_sugerencias_pdf/', views.reporte_quejas_sugerencias_pdf, name='reporte_quejas_sugerencias_pdf'),
    

]
