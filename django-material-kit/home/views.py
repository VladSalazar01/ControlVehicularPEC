from django.shortcuts import render, redirect, get_object_or_404
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
from django.contrib import messages


from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone

from django.http import FileResponse, HttpResponseRedirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from io import BytesIO
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger
from django.contrib.staticfiles import finders

from bs4 import BeautifulSoup
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from django.templatetags.static import static

from django.urls import reverse

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

    # Ruta absoluta a la imagen del encabezado
    image_path = finders.find('images/EscudonPNa.jpg')

    # Crea un PDF temporal con la imagen utilizando reportlab
    image_pdf = BytesIO()
    doc = SimpleDocTemplate(image_pdf, pagesize=letter)
    logo = Image(image_path, width=100, height=50) # Ajusta el tamaño según tus necesidades
    doc.build([logo])

    # HTML para el contenido del PDF, incluyendo la imagen
    html_content = f"""
        <img src="{image_path}" alt="Encabezado" width="50" /> POLICIA NACIONAL DEL ECUADOR<br>
        <h1>Parte Policial</h1>
        <p>Fecha: {parte.fecha}</p>
        <p>Tipo de Parte: {parte.tipo_parte}</p>
        <div>Observaciones: {parte.observaciones}</div>
        <p>Estado: {parte.estado}</p>
        <p>Firma de responsabilidad:</p>
        <p>Responsable: {personal_policial}</p>
        <p>Firma: ________________________</p>
    """

    # Crear un objeto PDF usando xhtml2pdf
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf)

    # Verifica si se produjo algún error
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF')

    # Devuelve el PDF como una respuesta
    pdf.seek(0)
    response = FileResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="parte_policial_{parte_id}.pdf"'

    return response

'''
def rechazar_parte(request, parte_id):
    parte = PartePolicial.objects.get(pk=parte_id)
    if parte.estado == 'En Proceso':
        parte.estado = 'Rechazado'
        parte.save()
    return HttpResponseRedirect(reverse('admin:home_partepolicial_changelist'))
'''

#ordenes de mantenimiento
def orden_mantenimiento_pdf(request, orden_mantenimiento_id):
    orden_mantenimiento = get_object_or_404(OrdenMantenimiento, id=orden_mantenimiento_id)
    parte_policial = orden_mantenimiento.parte_policial  # Obtener el PartePolicial asociado
        # Encontrar la ruta de la imagen
    image_path = finders.find('images/EscudonPNa.jpg')
    personal_policial = parte_policial.personalPolicial  # Obtener el PersonalPolicial asociado
    flota_vehicular = personal_policial.flota_vehicular  # Obtener el FlotaVehicular asociado
    usuario = personal_policial.usuario  # Este debería ser un objeto de Usuario
    user = usuario.user  # Este debería ser un objeto de User
    nombre_completo = f"{user.first_name} {user.last_name}"

    # Preparar el contexto
    context = {
        'image_path': image_path,

        'orden_mantenimiento': orden_mantenimiento,
        'kilometraje_actual': parte_policial.kilometraje_actual,
        'tipo_vehiculo': flota_vehicular.tipo_vehiculo,
        'numero_placa': flota_vehicular.placa,
        'marca': flota_vehicular.marca,
        'modelo': flota_vehicular.modelo,

        'id_responsable': personal_policial.id,  # Asumiendo que hay un campo 'id' en el modelo Usuario
        'nombre_completo': nombre_completo,
        'asunto': orden_mantenimiento.asunto,
        'detalle': orden_mantenimiento.detalle,


        'request': request
    }

    # Obtener la orden de mantenimiento
    orden_mantenimiento = OrdenMantenimiento.objects.get(id=orden_mantenimiento_id)
    # Renderizar la plantilla con la orden de mantenimiento
    template_path = 'Admin/orden_trabajo/orden_mantenimiento_pdf.html'
   # context = {'orden_mantenimiento': orden_mantenimiento, 'request': request}
    template = get_template(template_path)
    html = template.render(context)
    # Crear un objeto de archivo en memoria
    pdf_file = BytesIO()
    # Generar el PDF
    pisa_status = pisa.CreatePDF(
       html, dest=pdf_file)
    # Si el PDF se generó correctamente, enviarlo como respuesta HTTP
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF')
    else:
        pdf_file.seek(0, os.SEEK_SET)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orden_mantenimiento_{orden_mantenimiento_id}.pdf"'
        return response

def finalizar_orden_mantenimiento(request, orden_mantenimiento_id):
    orden_mantenimiento = get_object_or_404(OrdenMantenimiento, id=orden_mantenimiento_id)
    #parte_policial = get_object_or_404(Partepoli, id=orden_mantenimiento_id)
    if request.method == 'POST':
        form = FinalizarOrdenForm(request.POST)
        if form.is_valid():

            observaciones = form.cleaned_data['observaciones']
            orden_mantenimiento.estado = 'Despachada'
            if orden_mantenimiento.estado == 'Despachada':
                orden_mantenimiento.aprobador = request.user
            orden_mantenimiento.fecha_de_entrega = timezone.now()
            orden_mantenimiento.observaciones = observaciones

            # Actualizar el estado en PartePolicial
            parte_policial = orden_mantenimiento.parte_policial
            parte_policial.estado = 'Completado'
            parte_policial.save()

            # Actualizar el kilometraje en FlotaVehicular
            personal_policial = parte_policial.personalPolicial
            flota_vehicular = personal_policial.flota_vehicular
            flota_vehicular.kilometraje = orden_mantenimiento.kilometraje_actual
            flota_vehicular.save()

            orden_mantenimiento.save()
            
            messages.success(request, 'Orden de mantenimiento finalizada con éxito')
            messages.success(request, 'Parte Policial actualizado con éxito')
            messages.success(request, 'Kilometraje del vehículo actualizado con éxito')
            return redirect(reverse('admin:home_ordenmantenimiento_changelist'))
        else:
            return render(request, 'admin/orden_trabajo/finalizar_orden.html', {'form': form, 'orden': orden_mantenimiento})
    else:
        form = FinalizarOrdenForm()
        return render(request, 'admin/orden_trabajo/finalizar_orden.html', {'form': form, 'orden': orden_mantenimiento})
      

def descargar_pdf_orden_finalizada(request, orden_mantenimiento_id):
    orden_mantenimiento = get_object_or_404(OrdenMantenimiento, id=orden_mantenimiento_id)           
    
    parte_policial = orden_mantenimiento.parte_policial  # Obtener el PartePolicial asociado
        # Encontrar la ruta de la imagen
    image_path = finders.find('images/EscudonPNa.jpg')
    personal_policial = parte_policial.personalPolicial  # Obtener el PersonalPolicial asociado
    #flota_vehicular = personal_policial.flota_vehicular  # Obtener el FlotaVehicular asociado
    usuario = personal_policial.usuario  # Este debería ser un objeto de Usuario
    user = usuario.user  # Este debería ser un objeto de User
    nombre_completo = f"{user.first_name} {user.last_name}"

    flota_vehicular = personal_policial.flota_vehicular  # Aquí recuperamos el objeto FlotaVehicular asociado
    tipo_vehiculo = flota_vehicular.tipo_vehiculo  # Este debería ser 'Moto', 'Camioneta', o 'Auto'
        # Usamos el tipo de vehículo para determinar el kilometraje de la próxima revisión
    if tipo_vehiculo == 'Moto':
        kilometraje_proxima_revision = parte_policial.kilometraje_actual + 3000
    elif tipo_vehiculo in ['Camioneta', 'Auto']:
        kilometraje_proxima_revision = parte_policial.kilometraje_actual + 5000
    else:
        kilometraje_proxima_revision = "N/A"  # En caso de que tipo_vehiculo no esté definido o tenga un valor inesperado

    orden_mantenimiento.aprobador = request.user  # Suponiendo que el usuario que finaliza la orden es el aprobador
    

    orden_mantenimiento.save()       

    # Aquí, añade el código para generar el PDF como lo hiciste anteriormente.
    template_path = 'admin/orden_trabajo/orden_mantenimiento_finalizada_pdf.html'
    context = {
        'image_path': image_path,
        'parte_policial': parte_policial,  
        'orden_mantenimiento': orden_mantenimiento,

        'fecha_solicitud': parte_policial.fecha_solicitud,       
        'fecha': orden_mantenimiento.fecha_de_entrega,
        #'fecha_aprobacion': orden_mantenimiento.fecha, #(en plantilla)

        'nombre_completo': nombre_completo, #personal que entrega el vehiculo (autor del parte)
        #'nombre_completo': nombre_completo, #personal que entrega el vehiculo (posiblemente no el mismo autor de parte)
        'kilometraje_actual': parte_policial.kilometraje_actual, # refiere al de la revision (NC)
        #kilometraje de proximo mantenimiento (definido solo como +5k NC)
            
        #tipo de mantenimiento relizado esta definido en plantilla pero sin discriminante de tipo de vehiculo
        'kilometraje_proxima_revision': kilometraje_proxima_revision,  # Añadimos el nuevo valor al contexto
        'request': request
    }
    template = get_template(template_path)
    html = template.render(context)

    # Crear un objeto de archivo en memoria
    pdf_file = BytesIO()

    # Generar el PDF
    pisa_status = pisa.CreatePDF(
    html, dest=pdf_file)

    # Si el PDF se generó correctamente, enviarlo como respuesta HTTP
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF')
    else:
        pdf_file.seek(0)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orden_mantenimiento_finalizada_{orden_mantenimiento_id}.pdf"'
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