from django.urls import path
from . import views
from django.urls import path
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


]
