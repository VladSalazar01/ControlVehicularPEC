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

from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone

from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from io import BytesIO

from bs4 import BeautifulSoup
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from django.templatetags.static import static
from django.contrib.staticfiles import finders

import os
from django.conf import settings

from reportlab.lib.styles import getSampleStyleSheet

import re
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

#crear partes policiales (DEPRECACIÓN)   

#ver partes
@login_required
def mis_partes_policiales(request):
    usuario = Usuario.objects.get(user=request.user)
    personal_policial = PersonalPolicial.objects.get(usuario=usuario)
    partes_policiales_list = PartePolicial.objects.filter(personalPolicial=personal_policial)
    # Paginación
    paginator = Paginator(partes_policiales_list, 6) # Muestra 5 partes por página
    page = request.GET.get('page')
    try:
        partes_policiales = paginator.page(page)
    except PageNotAnInteger:      
        partes_policiales = paginator.page(1)
    except EmptyPage:     
        partes_policiales = paginator.page(paginator.num_pages)
    return render(request, 'partes_policiales/mis_partes_policiales.html', {'partes_policiales': partes_policiales})

#nuevo partes policiales
#agregar
#@method_decorator(login_required, name='dispatch') #repetida por accidente?
@method_decorator(login_required, name='dispatch')
class PartePolicialCreateView(CreateView):
    model = PartePolicial
    form_class = PartePolicialForm
    success_url = reverse_lazy('profile')  # redirige a la página de perfil después de la creación exitosa
    template_name = 'partes_policiales/parte_policial2.html'  # especifica la plantilla a utilizar

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})  # pasa el usuario al formulario
        return kwargs

    def form_valid(self, form):
        personal_policial = PersonalPolicial.objects.get(usuario__user=self.request.user)
        form.instance.personalPolicial = personal_policial
        form.instance.fecha = timezone.now()  # establece la fecha actual
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personal_policial = PersonalPolicial.objects.get(usuario__user=self.request.user)
        flota_vehicular = personal_policial.flota_vehicular
        context['vehiculo'] = flota_vehicular if flota_vehicular else "-Sin datos, contacte a logística-"
        context['subcircuito'] = flota_vehicular.subcircuito if flota_vehicular and flota_vehicular.subcircuito else "-Sin datos, contacte a logística-"
        context['fecha'] = timezone.now()  # establece la fecha actual en el contexto
        return context
    
def remove_html_tags(text):
    return re.sub('<[^>]*>', '', text)
@login_required
def parte_policial_pdf(request, parte_id):
    parte = PartePolicial.objects.get(id=parte_id)
    personal_policial = parte.personalPolicial.usuario.user.get_full_name()
    # Define la ruta relativa de la imagen dentro del directorio estático
    relative_path = 'images/EscudonPNa.jpg'

    # Concatena la ruta del directorio estático con la ruta relativa de la imagen
    image_path = os.path.join(settings.STATICFILES_DIRS[0], relative_path)
        
    # Crear un objeto Image
    logo = Image(image_path, width=50, height=50)  # Ajusta el tamaño según tus necesidades
    observaciones_plain_text = remove_html_tags(parte.observaciones)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    # Encabezado
    # Agregar la imagen al contenido
    content.append(logo)
    content.append(Paragraph("Parte Policial", styles['Heading1']))
    content.append(Spacer(1, 12))  # 12 puntos de espacio vertical
    # Detalles del Parte Policial
    content.append(Paragraph(f"Fecha: {parte.fecha}", styles['Normal']))
    content.append(Spacer(1, 12))  # 12 puntos de espacio vertical
    content.append(Paragraph(f"Tipo de Parte: {parte.tipo_parte}", styles['Normal']))
    content.append(Spacer(1, 12))  # 12 puntos de espacio vertical
    content.append(Paragraph(f"Observaciones: {observaciones_plain_text}", styles['Normal']))
    content.append(Spacer(1, 12))  # 12 puntos de espacio vertical
    content.append(Paragraph(f"Estado: {parte.estado}", styles['Normal']))
    content.append(Spacer(1, 24))  # 12 puntos de espacio vertical
    # Firma de responsabilidad
    content.append(Paragraph("Firma de responsabilidad:", styles['Normal']))
    content.append(Paragraph(f"Responsable: {personal_policial}", styles['Normal']))
    content.append(Spacer(1, 36))  # 12 puntos de espacio vertical
    content.append(Paragraph("Firma: ________________________", styles['Normal']))

    doc.build(content)

    buffer.seek(0)
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="parte_policial_{parte_id}.pdf"'

    return response


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

    template = get_template('admin/reportes_quejas/reporte_quejas_sugerencias.html')
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