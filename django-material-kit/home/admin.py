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
class CombinedAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'tipo_sangre', 'rango', 'identificacion', 'roles')
    def roles(self, obj):
        return ", ".join([group.name for group in obj.user.groups.all()])
    roles.short_description = 'Roles'
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Correo electrónico'
    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = 'Nombres'
    def last_name(self, obj):
        return obj.user.last_name
    last_name.short_description = 'Apellidos'
    def rango(self, obj):
        return obj.usuario.rango
    rango.short_description = 'Rango'
    def tipo_sangre(self, obj):
        return obj.tipo_sangre
    tipo_sangre.short_description = 'Tipo de sangre'
    def identificacion(self, obj):
        return obj.usuario.identificacion
    identificacion.short_description = 'Identificación'           

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add/', self.admin_site.admin_view(self.custom_add_view), name='custom-add'),
            path('<int:id>/change/', self.admin_site.admin_view(self.custom_change_view), name='custom-change'),  # Nueva vista de edición
        ]
        return custom_urls + urls
    
    def custom_change_view(self, request, id):
        usuario = Usuario.objects.get(id=id)
        user = usuario.user
        groups = user.groups.all() 
        try:
            tecnico = Tecnico.objects.get(usuario=usuario)
        except Tecnico.DoesNotExist:
            tecnico = None
        try:
            personal_policial = PersonalPolicial.objects.get(usuario=usuario)
        except PersonalPolicial.DoesNotExist:
            personal_policial = None

        if request.method == "POST":
            combined_form = CombinedForm(request.POST, instance=usuario)
            if combined_form.is_valid():
                user.username = combined_form.cleaned_data.get('username')                    
                user.email = combined_form.cleaned_data.get('email')
                user.password = combined_form.cleaned_data.get('password')
                user.first_name = combined_form.cleaned_data.get('first_name')
                user.last_name = combined_form.cleaned_data.get('last_name')
                user.save()
                usuario.tipo_sangre = combined_form.cleaned_data.get('tipo_sangre')
                usuario.save()

                new_groups = combined_form.cleaned_data.get('rol')
                user.groups.clear()  # Elimina todas las asignaciones de grupo existentes
                user.groups.add(*new_groups)  # Asigna los nuevos grupos

                if new_groups.filter(name='Tecnico').exists() and tecnico is not None:
                    tecnico.titular = combined_form.cleaned_data.get('titular')
                    tecnico.save()

                if new_groups.filter(name='PersonalPolicial').exists() and personal_policial is not None:
                    personal_policial.flota_vehicular = combined_form.cleaned_data.get('flota_vehicular')
                    personal_policial.turno_inicio = combined_form.cleaned_data.get('turno_inicio')
                    personal_policial.turno_fin = combined_form.cleaned_data.get('turno_fin')
                    personal_policial.save()

                messages.success(request, 'Usuario actualizado exitosamente')
                return redirect('admin:index')

        else:
            combined_form = CombinedForm(  
                instance=usuario,
                group_instance=groups,
                user_instance=user,
                tecnico_instance=tecnico,
                personal_policial_instance=personal_policial
            )
        return render(request, 'admin/custom_change_form.html', {
            'combined_form': combined_form,
            'user': user,
            'tecnico': tecnico,
            'personal_policial': personal_policial
        })

        
    def custom_add_view(self, request):
        if request.method == "POST":
            combined_form = CombinedForm(request.POST)

            if combined_form.is_valid():
                user = User.objects.create_user(
                    username=combined_form.cleaned_data.get('username'),
                    password=combined_form.cleaned_data.get('password'),
                    first_name=combined_form.cleaned_data.get('first_name'),
                    last_name=combined_form.cleaned_data.get('last_name'),
                    email=combined_form.cleaned_data.get('email')
                )
                usuario = combined_form.save(commit=False)
                usuario.user = user
                usuario.tipo_sangre = combined_form.cleaned_data.get('tipo_sangre')
                usuario.save()

                groups = combined_form.cleaned_data.get('rol')
                user.groups.add(*groups)  # Asigna los nuevos grupos

                if groups.filter(name='Tecnico').exists():
                    # Se seleccionó el rol 'Tecnico'
                    tecnico = Tecnico(usuario=usuario, titular=combined_form.cleaned_data.get('titular'))
                    tecnico.save()

                if groups.filter(name='PersonalPolicial').exists():
                    # Se seleccionó el rol 'PersonalPolicial'
                    personal_policial = PersonalPolicial(
                        usuario=usuario, 
                        flota_vehicular=combined_form.cleaned_data.get('flota_vehicular'),
                        turno_inicio=combined_form.cleaned_data.get('turno_inicio'),
                        turno_fin=combined_form.cleaned_data.get('turno_fin')
                    )
                    personal_policial.save()

                messages.success(request, 'Usuario creado exitosamente')
                return redirect('admin:index')

        else:
            combined_form = CombinedForm()

        return render(request, 'admin/custom_add_form.html', {
            'combined_form': combined_form
        })

    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, PersonalPolicial):
                if change:  # estamos actualizando un objeto existente
                    # obtén el objeto existente
                    original_obj = PersonalPolicial.objects.get(pk=instance.pk)
                    # si el usuario está cambiando, entonces actualiza el objeto existente en lugar de crear uno nuevo
                    if original_obj.usuario != instance.usuario:
                        original_obj.usuario = instance.usuario
                        original_obj.flota_vehicular = instance.flota_vehicular
                        original_obj.turno_inicio = instance.turno_inicio
                        original_obj.turno_fin = instance.turno_fin
                        original_obj.save()
                    else:  # estamos creando un nuevo objeto
                        instance.save()
                else:  # estamos creando un nuevo objeto
                    instance.save()
            else:
                instance.save()
        formset.save_m2m()
admin.site.register(Usuario, CombinedAdmin)
class PersonalPolicialInline(admin.TabularInline):
    model = PersonalPolicial
    extra = 0 

admin.site.register(PersonalPolicial, CombinedAdmin)
admin.site.register(Tecnico, CombinedAdmin)
admin.site.register(Rango_ctlg)
#admin.site.register(Subcircuitos)
#--fin personalizacion agregar  usuarios--


class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre','numero_de_distritos')
    def numero_de_distritos(self, obj):
        return obj.distritos.count()
    numero_de_distritos.short_description = 'Número de Distritos'
admin.site.register(Provincia, ProvinciaAdmin)

class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ('nombre','numero_de_subcircuitos')
    def numero_de_subcircuitos(self, obj):
        return obj.subcircuitos.count()
    numero_de_subcircuitos.short_description = 'Número de Subcircuitos'
admin.site.register(Parroquia, ParroquiaAdmin)


class DistritoAdmin(admin.ModelAdmin):
    list_display = ('cod_Distrito','provincia','nombre_Distrito', 'numero_de_circuitos')
    def numero_de_circuitos(self, obj):
        return obj.circuito.count()
    numero_de_circuitos.short_description = 'Número de Circuitos'
admin.site.register(Distrito, DistritoAdmin)

class CircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_Circuito','nombre_Circuito','numero_de_subcircuitos')
    def numero_de_subcircuitos(self, obj):
        return obj.subcircuito.count()
    numero_de_subcircuitos.short_description = 'Número de Subcircuitos'
admin.site.register(Circuito, CircuitoAdmin)

#display subcircuito (actualizar metodos PND, solo si van a ser usados en list_display)
class SubcircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_subcircuito','nombre_subcircuito')
class SubcircuitoInline(admin.StackedInline):

    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Subcircuitos, SubcircuitoAdmin)


class OrdendeTrabajoAdmin(admin.ModelAdmin):
    list_display = ('fecha','estado', 'tipo_orden', 'tecnico') 
    form = OrdenTrabajoForm

    def save_model(self, request, obj, form, change):
        obj.tecnico = request.user.usuario.tecnico
        super().save_model(request, obj, form, change)

admin.site.register(OrdendeTrabajo, OrdendeTrabajoAdmin)

class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo_mantenimiento','ordende_trabajo')  
admin.site.register(OrdenMantenimiento, OrdenMantenimientoAdmin)


admin.site.register(OrdenCombustible)

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

class FlotaVehicularAdmin(admin.ModelAdmin):
    inlines = [PersonalPolicialInline]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "personalpolicial":
            kwargs["queryset"] = PersonalPolicial.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
                
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
class PersonalPolicialAdmin(admin.ModelAdmin):
    list_display = ['usuario',  'flota_vehicular', 'turno_inicio', 'turno_fin']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flota_vehicular":
            kwargs["queryset"] = FlotaVehicular.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.unregister(PersonalPolicial)  # Desregistra el PersonalPolicial del CombinedAdmin
admin.site.register(PersonalPolicial, PersonalPolicialAdmin)  # Registra el PersonalPolicial con su propio ModelAdmin
#fin reescritura metodo save   


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

