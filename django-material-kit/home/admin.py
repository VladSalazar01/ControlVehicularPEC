from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging
from django.urls import reverse
from django.utils.html import format_html
import requests
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from nested_admin import NestedModelAdmin, NestedStackedInline
from django.utils import timezone


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
#admin.site.register(Subcircuitos)
#--fin personalizacion agregar  usuarios--




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

#----deprecar antiguo gest dependencias
'''
class CircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_Circuito','nombre_Circuito','numero_de_subcircuitos')    
    def numero_de_subcircuitos(self, obj):
        return obj.subcircuito.count()    
    numero_de_subcircuitos.short_description = 'Número de Subcircuitos'
admin.site.register(Circuito, CircuitoAdmin)

class SubcircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_subcircuito','nombre_subcircuito')
class SubcircuitoInline(admin.StackedInline):

admin.site.register(Subcircuitos, SubcircuitoAdmin)
'''


class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'creador_link', 'aprobador_link', 'fecha')
    readonly_fields = ('fecha',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # si la orden es nueva
            obj.creador = request.user
            obj.fecha = timezone.now()
        if 'estado' in form.changed_data and obj.estado == 'Despachada':  # si el estado ha cambiado a "Despachada"
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
class OrdenCombustibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'creador_link', 'aprobador_link', 'fecha')
    readonly_fields = ('fecha',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # si la orden es nueva
            obj.creador = request.user
            obj.fecha = timezone.now()
        if 'estado' in form.changed_data and obj.estado == 'Despachada':  # si el estado ha cambiado a "Despachada"
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

admin.site.register(OrdenMantenimiento, OrdenMantenimientoAdmin)
admin.site.register(OrdenCombustible, OrdenCombustibleAdmin)

#----deprecar antiguo gest oredens detrabajo
'''
class OrdendeTrabajoAdmin(admin.ModelAdmin):
    list_display = ('fecha','estado', 'tipo_orden', 'tecnico') 
    #form = OrdenTrabajoForm
    def save_model(self, request, obj, form, change):
        obj.tecnico = request.user.usuario.tecnico
        super().save_model(request, obj, form, change)
admin.site.register(OrdendeTrabajo, OrdendeTrabajoAdmin)

class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo_mantenimiento','ordende_trabajo')  
admin.site.register(OrdenMantenimiento, OrdenMantenimientoAdmin)
admin.site.register(OrdenCombustible)
'''

class PartePolicialAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo_parte', 'observaciones', 'estado', 'nombre_personal_policial')
    def nombre_personal_policial(self, obj):
        return obj.personalPolicial.usuario.user.username 
    nombre_personal_policial.short_description = 'Personal Policial'
admin.site.register(PartePolicial, PartePolicialAdmin)

class TallerMecanicoAdmin(admin.ModelAdmin):
    list_display = ('mecanico_responsable', 'nombre', 'direccion', 'telefono', 'tipo_taller')    
    def tipo_taller(self, obj):
        return dict(obj.sel_ttaller).get(obj.tipo_taller, obj.tipo_taller)
    tipo_taller.short_description = 'Tipo de Taller'
admin.site.register(TallerMecanico, TallerMecanicoAdmin)


class PersonalPolicialAdmin(admin.ModelAdmin):
    list_display = ['usuario',  'flota_vehicular', 'turno_inicio', 'turno_fin']
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
    list_display = ('marca', 'modelo', 'chasis', 'placa', 'kilometraje', 'subcircuito_cod', 'subcircuito_nombre', 'subcircuito_display')    
    # Método para mostrar el código del subcircuito 
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
''


'''
class PersonalPolicialInline(NestedTabularInline):
    model = PersonalPolicial
    extra = 0
'''
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

'''
    class Media:
        js = ('js/admin_autocomplete.js',)
'''



admin.site.register(Mantenimientos)

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

