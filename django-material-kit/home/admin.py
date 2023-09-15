from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path
from .models import *
from .views import *
from .forms import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging
from django.urls import reverse
from django.utils.html import format_html
import requests
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from nested_admin import NestedModelAdmin, NestedStackedInline
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime
from django.http import HttpResponseRedirect







def check_internet_connection():
    try:
        response = requests.get('https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/5UXWX7C5*BA?format=json', timeout=5)
        response.raise_for_status()
        print('Conexión exitosa.')
    except requests.exceptions.RequestException as err:
        print('Error al hacer la solicitud:', err)
    except requests.exceptions.HTTPError as http_err:
        print('HTTP error:', http_err)
    except requests.exceptions.ConnectionError as conn_err:
        print('Error de conexión:', conn_err)
    except requests.exceptions.Timeout as time_err:
        print('Timeout:', time_err)

check_internet_connection()

logger = logging.getLogger(__name__)
#grupos
class CustomPermissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CustomPermission, CustomPermissionAdmin)

#---personalizacion de admin panel para agregar usuarios---

admin.site.register(Rango_ctlg)



class ParroquiaInline(NestedStackedInline):
    list_display = ('nombre','numero_de_subcircuitos')
    model = Parroquia
    extra = 1 
    def numero_de_subcircuitos(self, obj):
        return obj.subcircuitos.count()
    numero_de_subcircuitos.short_description = 'Número de Subcircuitos'
#admin.site.register(Parroquia, )
class ProvinciaAdmin(NestedModelAdmin):
    list_display = ('nombre','numero_de_distritos')
    inlines = [ParroquiaInline]
    def numero_de_distritos(self, obj):
        return obj.distritos.count()
    numero_de_distritos.short_description = 'Número de Distritos'
admin.site.register(Provincia, ProvinciaAdmin)

class SubcircuitoInline(NestedStackedInline):
    model = Subcircuitos
    extra = 1
    classes = ['subcircuito-inline']  

class CircuitoInline(NestedStackedInline):
    list_display = ('cod_Circuito','nombre_Circuito','numero_de_subcircuitos')
    model = Circuito
    extra = 1
    inlines = [SubcircuitoInline]
    def numero_de_subcircuitos(self, obj):
        return obj.subcircuito.count()
    numero_de_subcircuitos.short_description = 'Número de Subcircuitos'
    class Media:
        js = ('js/admin_dependencias.js',) 
class DistritoAdmin(NestedModelAdmin):
    list_display = ('cod_Distrito','provincia','nombre_Distrito', 'numero_de_circuitos')
    inlines = [CircuitoInline]
    def numero_de_circuitos(self, obj):
        return obj.circuito.count()
    numero_de_circuitos.short_description = 'Número de Circuitos'
    class Media:
        js = ('js/admin_dependencias.js',)  
admin.site.register(Distrito, DistritoAdmin)


class OrdenMantenimientoAdmin(admin.ModelAdmin):
    change_form_template = 'admin/orden_trabajo/ordenmantenimiento_change_form.html'
    change_list_template = 'admin/orden_trabajo/ordenmantenimiento_change_list.html'

    #search_fields = ['fecha', 'tipos_mantenimiento__tipo', 'creador__username', 'aprobador__username', 'estado']

    list_filter = ['fecha', 'tipos_mantenimiento', 'creador', 'aprobador']
    list_display = ('fecha','fecha_de_entrega', 'get_tipo_mantenimiento', 'estado', 'creador', 'aprobador', 'ver_parte_asociado','pdf_link','finalizar_orden_link', 'descargar_pdf_link',)
    fecha = models.DateField(auto_now_add=True)
    form = OrdenMantenimientoForm
    readonly_fields = ('creador', 'aprobador', 'fecha',)

    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creador = request.user
            obj.fecha = datetime.date.today()
        obj.aprobador = request.user
        super().save_model(request, obj, form, change)

    def get_tipo_mantenimiento(self, obj):
        return ', '.join([tipo.tipo for tipo in obj.tipos_mantenimiento.all()])
    get_tipo_mantenimiento.short_description = 'Tipos de Mantenimiento'
    

    
    def finalizar_orden_link(self, obj):
        if obj.estado == "Activa":
            return format_html('<a class="button" href="{}">Finalizar orden de trabajo</a>',
    reverse('finalizar_orden_mantenimiento', args=[obj.pk]))
        else:
            return "No disponible"
    finalizar_orden_link.short_description = "Finalizar Orden"

    def descargar_pdf_link(self, obj):
        if obj.estado == "Despachada":
            return format_html('<a class="button" href="{}">Descargar PDF Orden Finalizada</a>',
    reverse('descargar_pdf_orden_finalizada', args=[obj.pk]))
        else:
            return "No disponible"
    descargar_pdf_link.short_description = "Descargar PDF"      
    
    def ver_parte(self, request, orden_mantenimiento_id):
        orden = OrdenMantenimiento.objects.get(id=orden_mantenimiento_id)
        parte = orden.parte_asociado
        # Lógica para visualizar el archivo (puede variar según tus necesidades)
        return HttpResponseRedirect(parte.url)
    
    def ver_parte_asociado(self, obj):
        return format_html('<a href="{}" target="_blank">Ver parte asociado</a>', reverse('admin:ver_parte', args=[obj.id]))
    ver_parte_asociado.short_description = 'Ver parte asociado'

    def create_ordenmantenimiento(self, request):
        if request.method == 'POST':
            form = OrdenMantenimientoForm(request.POST)
            if form.is_valid():
                ordenmantenimiento = form.save()
                return redirect('admin:update_ordenmantenimiento', ordenmantenimiento_id=ordenmantenimiento.id)
        else:
            form = OrdenMantenimientoForm()
        return render(request, 'admin/orden_trabajo/create_ordenmantenimiento.html', {'form': form})

    def update_ordenmantenimiento(self, request, ordenmantenimiento_id):
        ordenmantenimiento = OrdenMantenimiento.objects.get(id=ordenmantenimiento_id)
        if request.method == 'POST':
            form = TipoMantenimientoForm(request.POST, instance=ordenmantenimiento)
            if form.is_valid():
                form.save()
                return redirect('admin:home_ordenmantenimiento_changelist')
        else:
            form = TipoMantenimientoForm(instance=ordenmantenimiento)
        return render(request, 'admin/orden_trabajo/update_ordenmantenimiento.html', {'form': form, 'ordenmantenimiento': ordenmantenimiento})
    
    def save_model(self, request, obj, form, change):
        if not change:  # sólo para nuevos objetos, no para los ya existentes
            obj.creador = request.user
        if obj.estado == 'Despachada':
            obj.aprobador = request.user
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipos_mantenimiento'] = TipoMantenimiento.objects.all()
        return super().changelist_view(request, extra_context=extra_context)
    
    def pdf_link(self, obj):
        url = reverse('orden_mantenimiento_pdf', args=[obj.pk])
        return format_html('<a href="{}">Emitir orden de Mantenimiento</a>', url)
    pdf_link.short_description = "Orden de Mantenimiento PDF"

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrdenMantenimientoAdmin, self).get_form(request, obj, **kwargs)
        if obj is None or obj.estado != 'Despachada':  # Puede ajustar la condición según su caso de uso
            form.base_fields['observaciones'].widget = forms.HiddenInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create/', self.create_ordenmantenimiento, name='create_ordenmantenimiento'),
            path('<int:ordenmantenimiento_id>/update/', self.update_ordenmantenimiento, name='update_ordenmantenimiento'),
            path('<int:orden_mantenimiento_id>/ver_parte/', self.ver_parte, name='ver_parte'),
            path('<int:orden_mantenimiento_id>/finalizar/', self.admin_site.admin_view(finalizar_orden_mantenimiento), name='finalizar_orden_mantenimiento'),
            path('<int:orden_mantenimiento_id>/descargar/', self.admin_site.admin_view(descargar_pdf_orden_finalizada), name='descargar_pdf_orden_finalizada'),
        ]
        return custom_urls + urls
admin.site.register(OrdenMantenimiento, OrdenMantenimientoAdmin)

class OrdenCombustibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'creador_link', 'aprobador_link', 'fecha')
    readonly_fields = ('fecha',)
    search_fields = ['fecha', 'tipo_de_combustible', 'creador__username', 'aprobador__username']
    list_filter = ['fecha', 'tipo_de_combustible']
    readonly_fields = ['creador', 'aprobador']
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # si la orden es nueva
            obj.creador = request.user
            obj.fecha = timezone.now()
        if 'estado' in form.changed_data and obj.estado == 'Despachada':  
            obj.aprobador = request.user
        super().save_model(request, obj, form, change)


    def creador_link(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.creador.id])
        return format_html('<a href="{}">{}</a>', link, obj.creador.username)
    creador_link.short_description = 'Creado por'
    def aprobador_link(self, obj):
        if obj.aprobador:
            link = reverse("admin:auth_user_change", args=[obj.aprobador.id])
            return format_html('<a href="{}">{}</a>', link, obj.aprobador.username)
        return "-"
    aprobador_link.short_description = 'Aprobado por'

admin.site.register(OrdenCombustible, OrdenCombustibleAdmin)


class PartePolicialAdmin(admin.ModelAdmin):
    list_filter = ['fecha', 'tipo_parte',  'estado', 'personalPolicial__usuario__user__username']
    list_display = ('fecha', 'tipo_parte', 'observaciones', 'estado', 'nombre_personal_policial', 'rechazar_parte')
    readonly_fields = ['personalPolicial', 'fecha']

    def nombre_personal_policial(self, obj):
        return obj.personalPolicial.usuario.user.username 
    nombre_personal_policial.short_description = 'Personal Policial'

    def rechazar_parte(self, obj):
        if obj.estado == 'En Proceso':
            return format_html(
                '<a class="button" href="{}">Rechazar Parte</a>',
                reverse('admin:set_rechazado', args=[obj.pk])
            )
        else:
            return "No se puede rechazar"
    rechazar_parte.short_description = 'Rechazar Parte'
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('set_rechazado/<int:parte_id>/', self.admin_site.admin_view(self.set_rechazado), name='set_rechazado'),
        ]
        return my_urls + urls

    def set_rechazado(self, request, parte_id):
        obj = PartePolicial.objects.get(pk=parte_id)
        obj.estado = 'Rechazado'
        obj.save()
        return HttpResponseRedirect("../../")
admin.site.register(PartePolicial, PartePolicialAdmin)

class TallerMecanicoAdmin(admin.ModelAdmin):
    list_display = ('mecanico_responsable', 'nombre', 'direccion', 'telefono', 'tipo_taller')    
    def tipo_taller(self, obj):
        return dict(obj.sel_ttaller).get(obj.tipo_taller, obj.tipo_taller)
    tipo_taller.short_description = 'Tipo de Taller'
admin.site.register(TallerMecanico, TallerMecanicoAdmin)

class SubcircuitoForm(forms.Form):
    subcircuito = forms.ModelChoiceField(queryset=Subcircuitos.objects.all())
class PersonalPolicialAdmin(admin.ModelAdmin):
    list_display = ['usuario',  'flota_vehicular', 'turno_inicio', 'turno_fin','subcircuito',]
    list_filter = ['usuario', 'flota_vehicular', 'subcircuito']
    actions = ['asignar_subcircuito']

    def asignar_subcircuito(self, request, queryset):
        selected = request.POST.getlist('_selected_action')
        subcircuitos = Subcircuitos.objects.all()
        return render(request, 'admin/asign_bulk_s/asignar_subcircuito.html', {'personalpoliciales': selected, 'subcircuitos': subcircuitos})

    asignar_subcircuito.short_description = "Asignar personal policial a subcircuitos"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('asignar-subcircuito-perpol/', self.admin_site.admin_view(self.asignar_subcircuito_view_per_pol), name='asignar-subcircuito-per-pol'),
        ]
        return custom_urls + urls

    def asignar_subcircuito_view_per_pol(self, request):
        if request.method == 'POST':
            subcircuito_id = request.POST.get('subcircuito')
            personalpolicial_ids = request.POST.getlist('personalpoliciales')

            print(f"Subcircuito ID: {subcircuito_id}")
            print(f"Personalpolicial IDs: {personalpolicial_ids}")

            subcircuito = Subcircuitos.objects.get(id=subcircuito_id)
            personalpoliciales = PersonalPolicial.objects.filter(id__in=personalpolicial_ids)
            
            for personalpolicial in personalpoliciales:
                personalpolicial.subcircuito = subcircuito
                personalpolicial.save()
            
            self.message_user(request, 'Subcircuito asignado con éxito')
            return redirect('..')
        subcircuitos = Subcircuitos.objects.all()
        return render(request, 'admin/asign_bulk_s/asignar_subcircuito.html', {'subcircuitos': subcircuitos})
   

    '''
    def asignar_subcircuito(self, request, queryset):
        print(request.POST)  # Agrega esta línea
        form = SubcircuitoForm(request.POST or None)
        
        if form.is_valid():
            subcircuito = form.cleaned_data['subcircuito']
            selected = PersonalPolicial.objects.filter(id__in=request.POST.getlist('selected_action'))
            count = selected.update(subcircuito=subcircuito)
            self.message_user(request, f'Se han asignado {count} personal policial al subcircuito {subcircuito}.')
            return HttpResponseRedirect(reverse('admin:home_personalpolicial_changelist'))
        else:
            print(form.errors)  # Agrega esta línea
        return render(request, 'admin/asign_bulk_s/asignar_subcircuito.html', {'personal': queryset, 'form': form})
    asignar_subcircuito.short_description= 'Asignar Subcircuito a Personal Policial seleccionado'
    '''


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flota_vehicular":
            kwargs["queryset"] = FlotaVehicular.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PersonalPolicialInline(admin.TabularInline):
    model = PersonalPolicial
    extra = 0
admin.site.register(PersonalPolicial, PersonalPolicialAdmin)  

class FlotaVehicularAdmin(admin.ModelAdmin):
    inlines = [PersonalPolicialInline]                 
    class Media:
            js = ('js/flotavehicular.js',) 

    list_filter = ['marca', 'modelo', 'chasis', 'placa', 'kilometraje', 'subcircuito__cod_subcircuito', 'subcircuito__nombre_subcircuito']        
    list_display = ('marca', 'modelo', 'chasis', 'placa', 'kilometraje', 'subcircuito_cod', 'subcircuito_nombre', 'subcircuito_display')    
    actions = ['asignar_subcircuito']

    def asignar_subcircuito(self, request, queryset):
        selected = request.POST.getlist('_selected_action')
        subcircuitos = Subcircuitos.objects.all()
        return render(request, 'admin/asign_bulk_s/asignar_subcircuito_v.html', {'flotas': selected, 'subcircuitos': subcircuitos})

    asignar_subcircuito.short_description = "Asignar subcircuito a flotas seleccionadas"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('asignar-subcircuito/', self.admin_site.admin_view(self.asignar_subcircuito_view), name='asignar-subcircuito'),
        ]
        return custom_urls + urls

    def asignar_subcircuito_view(self, request):
        if request.method == 'POST':
            subcircuito_id = request.POST.get('subcircuito')
            flotas_ids = request.POST.getlist('flotas')

            print(f"Subcircuito ID: {subcircuito_id}")
            print(f"Flotas IDs: {flotas_ids}")

            subcircuito = Subcircuitos.objects.get(id=subcircuito_id)
            flotas = FlotaVehicular.objects.filter(id__in=flotas_ids)
            
            for flota in flotas:
                flota.subcircuito = subcircuito
                flota.save()
            
            self.message_user(request, 'Subcircuito asignado con éxito')
            return redirect('..')
        subcircuitos = Subcircuitos.objects.all()
        return render(request, 'admin/asign_bulk_s/asignar_subcircuito_v.html', {'subcircuitos': subcircuitos})

    def subcircuito_display(self, obj):
        return obj.subcircuito.nombre_subcircuito
    subcircuito_display.short_description = 'Subcircuito'

    def subcircuito_cod(self, obj):
        return obj.subcircuito.cod_subcircuito
    subcircuito_cod.short_description = 'Código Subcircuito' 

    def subcircuito_nombre(self, obj):
        return obj.subcircuito.nombre_subcircuito 
    subcircuito_nombre.short_description = 'Nombre Subcircuito'
admin.site.register(FlotaVehicular, FlotaVehicularAdmin)

class UsuarioInline(NestedStackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Información de usuario'
    #inlines = [PersonalPolicialInline]
class UserAdmin(BaseUserAdmin, NestedModelAdmin):
    inlines = [UsuarioInline]
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ('nombres','apellidos')
    def nombres(self, obj):
        return obj.usuario.user.first_name
    nombres.short_description = 'Nombres'
    def apellidos(self, obj):
        return obj.usuario.user.last_name
    apellidos.short_description = 'Apellidos' 
#admin.site.register(PersonalPolicial, CombinedAdmin)
admin.site.register(Tecnico, TecnicoAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Mantenimientos)



class TipoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo','descripcion', 'costo')
admin.site.register(TipoMantenimiento, TipoMantenimientoAdmin)

#EVALUACIÓN buzon de quejas
class QuejaSugerenciaAdmin(admin.ModelAdmin):   
    list_display = ('fecha_creacion','tipo', 'nombres', 'apellidos', 'circuito',  'subcircuito') 
    readonly_fields = ('fecha_creacion',)
    change_list_template = 'admin/reportes_quejas/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['reporte_url'] = reverse('reporte_quejas_sugerencias')
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(QuejaSugerencia, QuejaSugerenciaAdmin)

