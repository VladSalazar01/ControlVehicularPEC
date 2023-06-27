from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('iniciar_sesion/', views.user_login, name='iniciar_sesion'),
]
