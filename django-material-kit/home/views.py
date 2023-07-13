from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import *
from datetime import date
from django.http import JsonResponse
from django.db.models import F, Value, CharField, Count
from django.db.models.functions import Concat
from django.contrib.admin.views.decorators import staff_member_required
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context

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
    partes_policiales_list = PartePolicial.objects.filter(personalPolicial=personal_policial)
    # Paginación
    paginator = Paginator(partes_policiales_list, 3) # Muestra 5 partes por página
    page = request.GET.get('page')
    try:
        partes_policiales = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        partes_policiales = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, entrega la última página de resultados.
        partes_policiales = paginator.page(paginator.num_pages)
    return render(request, 'partes_policiales/mis_partes_policiales.html', {'partes_policiales': partes_policiales})

#EVALUACION
def queja_sugerencia(request):
    if request.method == 'POST':
        form = QuejaSugerenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'quejas/agradecimiento.html')
    else:
        form = QuejaSugerenciaForm()
    return render(request, 'quejas/queja_sugerencia.html', {'form': form})

def get_subcircuitos(request, circuito_id):
    subcircuitos = Subcircuitos.objects.filter(subcircuitoCircuito=circuito_id).annotate(cod_nombre=Concat(F('cod_subcircuito'), Value(', '), F('nombre_subcircuito'), output_field=CharField())).values('id', 'cod_nombre')
    subcircuito_list = list(subcircuitos)
    return JsonResponse(subcircuito_list, safe=False)

@staff_member_required
def reporte_quejas_sugerencias(request):
    inicio = request.GET.get('fecha_inicio')
    fin = request.GET.get('fecha_fin')
    quejas_sugerencias = QuejaSugerencia.objects.all()
    if inicio and fin:
        quejas_sugerencias = quejas_sugerencias.filter(fecha_creacion__range=[inicio, fin])
    quejas_sugerencias = quejas_sugerencias.values('circuito__nombre_Circuito', 'subcircuito__nombre_subcircuito', 'tipo').annotate(total=Count('id'))
    return render(request, 'admin/reportes_quejas/reporte_quejas_sugerencias.html', {'quejas_sugerencias': quejas_sugerencias})


@staff_member_required
def reporte_quejas_sugerencias_pdf(request):
    inicio = request.GET.get('fecha_inicio')
    fin = request.GET.get('fecha_fin')
    quejas_sugerencias = QuejaSugerencia.objects.all()
    if inicio and fin:
        quejas_sugerencias = quejas_sugerencias.filter(fecha_creacion__range=[inicio, fin])
    quejas_sugerencias = quejas_sugerencias.values('circuito__nombre_Circuito', 'subcircuito__nombre_subcircuito', 'tipo').annotate(total=Count('id'))

    template = get_template('admin/reporte_quejas_sugerencias.html')
    html = template.render(Context({'quejas_sugerencias': quejas_sugerencias, 'fecha_inicio': inicio, 'fecha_fin': fin, 'usuario': request.user}))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
       return HttpResponse('Hubo un error al generar el reporte PDF <pre>' + html + '</pre>')
    return response



#EVALUACION
#--agregar usuario desde admin panel------
'''def custom_add_view(self, request):
    if request.method == "POST":
        combined_form = CombinedForm(request.POST)

        if combined_form.is_valid():
            user = User.objects.create_user(
                username=combined_form.cleaned_data.get('username'),
                password=combined_form.cleaned_data.get('password'),
                first_name=combined_form.cleaned_data.get('first_name'),
                last_name=combined_form.cleaned_data.get('last_name')
            )
            usuario = combined_form.save(commit=False)
            usuario.user = user
            usuario.save()

            role = combined_form.cleaned_data.get('role')
            if role == 'personal_policial':
                PersonalPolicial.objects.create(
                    usuario=usuario,
                    subcircuito=combined_form.cleaned_data.get('subcircuito')
                )
            elif role == 'tecnico':
                Tecnico.objects.create(
                    usuario=usuario,
                    titular=combined_form.cleaned_data.get('titular')
                )

            return redirect('admin:index')

    else:
        combined_form = CombinedForm()

    return render(request, 'admin/custom_add_form.html', {
        'combined_form': combined_form
    })'''