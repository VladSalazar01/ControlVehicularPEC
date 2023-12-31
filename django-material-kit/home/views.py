from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import *
from datetime import date, datetime


from django.db.models import F, Value, CharField, Count
from django.db.models.functions import Concat
from django.contrib.admin.views.decorators import staff_member_required
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from dateutil.parser import parse

import pandas as pd
import csv
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt


from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy


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

    # Inicialización de los filtros
    fecha_filter = request.GET.get('fecha')
    tipo_parte_filter = request.GET.get('tipo_parte')
    estado_filter = request.GET.get('estado')
    
    # Filtrado de los objetos
    partes_policiales_list = PartePolicial.objects.filter(personalPolicial=personal_policial)
    
    if fecha_filter:
        partes_policiales_list = partes_policiales_list.filter(fecha=fecha_filter)
    
    if tipo_parte_filter:
        partes_policiales_list = partes_policiales_list.filter(tipo_parte=tipo_parte_filter)
        
    if estado_filter:
        partes_policiales_list = partes_policiales_list.filter(estado=estado_filter)


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
    

    # Obtén los tipos de mantenimiento seleccionados para esta orden
    tipos_seleccionados = orden_mantenimiento.tipos_mantenimiento.all()
    # Obtén el objeto PersonalPolicial relacionado con el PartePolicial
    personal_policial = parte_policial.personalPolicial
    # Obtén el objeto FlotaVehicular relacionado con el PersonalPolicial
    #flota_vehicular = personal_policial.flota_vehicular
    # Ahora puedes acceder al tipo de vehículo
    #tipo_vehiculo = flota_vehicular.tipo_vehiculo
    # Inicializa variables para mantener el subtotal y las descripciones
    subtotal_general = 0
    descripcion_general = []
    # Itera sobre cada tipo de mantenimiento seleccionado
    for tipo in tipos_seleccionados:
        # Aquí asumimos que el modelo TipoMantenimiento tiene campos 'descripcion' y 'costo'
        descripcion = tipo.descripcion.splitlines()  # Supongamos que guardas cada item en una nueva línea
        costo = tipo.costo
        # Si se selecciona M2, ajusta la descripción y el costo según el tipo de vehículo
        if tipo.tipo == 'M2':
            if tipo_vehiculo in ['Auto', 'Camioneta']:
                descripcion = tipo.descripcion.splitlines()
                costo = tipo.costo
            elif tipo_vehiculo == 'Moto':
                descripcion = tipo.descripcion.splitlines()
                costo = tipo.costo-15  # Asume que este costo es diferente para 'Moto'
        subtotal_general += costo
        descripcion_general.extend(descripcion)
    # Calcula el IVA y el total
    iva = (subtotal_general * Decimal(0.12)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    total = (subtotal_general + iva).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    subtotal_general = subtotal_general.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

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

        'descripcion_general': descripcion_general,
        'tipo_vehiculo': flota_vehicular.tipo_vehiculo,
        'subtotal_general': subtotal_general,
        'iva': iva,
        'total': total,
        
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

#rebuild de asignación de personal a flota vehicular -admin
def asignar_personal_policial(request, flota_id):
    flota = FlotaVehicular.objects.get(id=flota_id)
    if request.method == "POST":
        personal_ids = request.POST.getlist('personal_policial')
        personal_asignado = PersonalPolicial.objects.filter(id__in=personal_ids)
        for personal in personal_asignado:
            turno_inicio = request.POST.get(f'turno_inicio_{personal.id}')
            turno_fin = request.POST.get(f'turno_fin_{personal.id}')
            if turno_inicio and turno_fin:
                personal.turno_inicio = turno_inicio
                personal.turno_fin = turno_fin
            personal.flota_vehicular = flota
            personal.save()
        return redirect(reverse('admin:home_flotavehicular_change', args=[flota.id]))
    
    personal_disponible = PersonalPolicial.objects.all()
    personal_asignado = PersonalPolicial.objects.filter(flota_vehicular=flota)
    personal_asignado_ids = personal_asignado.values_list('id', flat=True)  # Obtener los IDs como una lista
    
    return render(request, 'admin/flota_vehicular/asignar_personal_policial.html', {
        'flota': flota,
        'personal_disponible': personal_disponible,
        'personal_asignado_ids': personal_asignado_ids,
        'personal_asignado': personal_asignado,
    })



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

    # Convertir las fechas a datetime aware
    if inicio:
        inicio = timezone.make_aware(datetime.strptime(inicio, '%Y-%m-%d'))
    if fin:
        fin = timezone.make_aware(datetime.strptime(fin, '%Y-%m-%d'))

    quejas_sugerencias = QuejaSugerencia.objects.all()

    if inicio and fin:
        quejas_sugerencias = quejas_sugerencias.filter(fecha_creacion__range=[inicio, fin])

    quejas_sugerencias = quejas_sugerencias.values('circuito__nombre_Circuito', 'subcircuito__nombre_subcircuito', 'tipo').annotate(total=Count('id'))

    return render(request, 'admin/reportes_quejas/reporte_quejas_sugerencias.html', {'quejas_sugerencias': quejas_sugerencias, 'fecha_inicio': inicio, 'fecha_fin': fin, 'usuario': request.user})


def parse_custom_date(date_str):
    match = re.search(r'(\d+) de (\w+) de (\d+) a las (\d+):(\d+)', date_str)
    if not match:
        return None
    
    day, month_str, year, hour, minute = match.groups()
    month_str = month_str.lower()
    month_dict = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 
                  'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 
                  'octubre': 10, 'noviembre': 11, 'diciembre': 12}
    
    month = month_dict.get(month_str)
    if month is None:
        return None
    
    try:
        date_obj = datetime(year=int(year), month=month, day=int(day), 
                            hour=int(hour), minute=int(minute))
        return timezone.make_aware(date_obj)
    except ValueError:
        return None


@staff_member_required
def reporte_quejas_sugerencias_export(request):
    print(f"Initial request.GET: {request.GET}")  # Debugging
    formato = request.GET.get('formato', 'pdf')
    inicio_str = request.GET.get('fecha_inicio')
    fin_str = request.GET.get('fecha_fin')
    inicio=None
    fin=None
    print(f"Initial dates: {inicio_str}, {fin_str}")  # Debugging

    if inicio_str:
        inicio = parse_custom_date(inicio_str)
    
    if fin_str:
        fin = parse_custom_date(fin_str)

    print(f"Parsed dates: {inicio}, {fin}")  # Debugging
    # Convertir las fechas a datetime aware, exactamente como en reporte_quejas_sugerencias
 
    quejas_sugerencias = QuejaSugerencia.objects.all()

    if inicio and fin:
        quejas_sugerencias = quejas_sugerencias.filter(fecha_creacion__range=[inicio, fin])

    quejas_sugerencias = quejas_sugerencias.values('circuito__nombre_Circuito', 'subcircuito__nombre_subcircuito', 'tipo').annotate(total=Count('id'))

    df = pd.DataFrame.from_records(quejas_sugerencias)

    if formato == 'pdf':
        template = get_template('admin/reportes_quejas/reporte_quejas_sugerencias_export.html')
        context = {
            'quejas_sugerencias': quejas_sugerencias,
            'fecha_inicio': inicio,
            'fecha_fin': fin,
            'usuario': request.user,
        }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Hubo un error al generar el reporte PDF <pre>' + html + '</pre>')
    
    elif formato == 'xls':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="reporte.xls"'
        df.to_excel(response, index=False)

    elif formato == 'xml':
        response = HttpResponse(df.to_xml(), content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="reporte.xml"'

    elif formato == 'csv':
        response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte.csv"'

    elif formato in ['jpeg', 'png']:
        plt.figure(figsize=(10, 4))
        df.plot(kind='bar')
        img_io = BytesIO()
        plt.savefig(img_io, format=formato)
        img_io.seek(0)
        response = HttpResponse(img_io.read(), content_type=f'image/{formato}')
        response['Content-Disposition'] = f'attachment; filename=reporte.{formato}'
        img_io.close()

    return response
#EVALUACION

#exacomplex exect
@login_required
def crear_orden_movilizacion(request):
    if request.method == 'POST':
        form = OrdenMovilizacionForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            personal_policial = PersonalPolicial.objects.get(usuario__user=request.user)
            orden.personal_policial_solicitante = personal_policial
            orden.save()
            return redirect('numero_ocupantes', orden_id=orden.id)  
    else:
        form = OrdenMovilizacionForm()
    return render(request, 'orden_mov/orden_mov_formu.html', {'form': form})

@login_required
def numero_ocupantes(request, orden_id):
    orden = OrdenMovilizacion.objects.get(id=orden_id)
    if request.method == 'POST':
        form = NumeroOcupantesForm(request.POST)
        if form.is_valid():
            orden.numero_ocupantes = form.cleaned_data['numero_ocupantes']
            orden.save()
            return redirect('seleccionar_ocupantes', orden_id=orden.id)
    else:
        form = NumeroOcupantesForm()
    return render(request, 'orden_mov/numero_ocupantes.html', {'form': form, 'orden': orden})

@login_required
def seleccionar_ocupantes(request, orden_id):
    orden = OrdenMovilizacion.objects.get(id=orden_id)
    max_ocupantes = orden.numero_ocupantes  
    
    if request.method == 'POST':
        form = SeleccionarOcupantesForm(max_ocupantes, request.POST)
        if form.is_valid():
            orden.ocupantes.set(form.cleaned_data['ocupantes'])
            return redirect('profile')
    else:
        form = SeleccionarOcupantesForm(max_ocupantes)
        
    return render(request, 'orden_mov/seleccionar_ocupantes.html', {'form': form, 'orden': orden})

