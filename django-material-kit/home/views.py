from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import *
from .models import *
from datetime import date

# Create your views here.

def index(request):
    # Page from the theme 
    return render(request, 'pages/index.html')


def welcome(request):
    return render(request, 'inicio/welcome.html')

# Vista para el inicio de sesión[USO DEPRECADO POR SOBREINGENIERÍA]
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio/profile.html')  # Redirige a la página de bienvenida después de iniciar sesión
        else:
            # Retorna un mensaje de error si la autenticación falla
            return render(request, 'inicio/sign-in[n].html', {'error': 'Nombre de usuario o contraseña inválidos'})
    return render(request, 'inicio/sign-in[n].html')

# Vista para la página de perfil
@login_required
def profile(request):
    return render(request, 'inicio/profile.html')

#crear partes policiales
@login_required
def parte_policial(request):
    if request.method == 'POST':
        form = PartePolicialForm(request.POST)
        if form.is_valid():
            parte_policial = form.save(commit=False)
            usuario = Usuario.objects.get(user=request.user)
            parte_policial.personalPolicial = PersonalPolicial.objects.get(usuario=usuario)
            # Establecer la fecha al día actual
            parte_policial.fecha = date.today()
            parte_policial.save()
            return redirect('status', status='success')
        else:
            return redirect('status', status='error')
    else:
        form = PartePolicialForm()
    return render(request, 'partes_policiales/parte_policial.html', {'form': form, 'fecha': date.today()})

@login_required
def status(request, status):
    return render(request, 'partes_policiales/status.html', {'status': status})
#ver partes
@login_required
def mis_partes_policiales(request):
    usuario = Usuario.objects.get(user=request.user)
    personal_policial = PersonalPolicial.objects.get(usuario=usuario)
    partes_policiales = PartePolicial.objects.filter(personalPolicial=personal_policial)
    return render(request, 'partes_policiales/mis_partes_policiales.html', {'partes_policiales': partes_policiales})