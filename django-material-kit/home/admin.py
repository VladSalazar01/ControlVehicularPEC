from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path
from .models import *
from django.shortcuts import render, redirect
from .forms import CombinedForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging
from django.urls import reverse
from django.utils.html import format_html




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
                identificacion = combined_form.cleaned_data.get('identificacion')

                if Usuario.objects.filter(identificacion=identificacion).exclude(id=usuario.id).exists():
                    messages.error(request, 'La identificación ya está en uso.')
                else:
                    user.username = combined_form.cleaned_data.get('username')                    
                    user.email = combined_form.cleaned_data.get('email')
                    user.password = combined_form.cleaned_data.get('password')
                    user.first_name = combined_form.cleaned_data.get('first_name')
                    user.last_name = combined_form.cleaned_data.get('last_name')
                    user.save()
                    usuario.tipo_sangre = combined_form.cleaned_data.get('tipo_sangre')  
                    usuario.rango = combined_form.cleaned_data.get('rango')
                    usuario.save()
                    new_groups = combined_form.cleaned_data.get('rol')
                    if new_groups.filter(name='Tecnico').exists() and tecnico is not None:
                        tecnico.titular = combined_form.cleaned_data.get('titular')
                        tecnico.save()
                    if new_groups.filter(name='PersonalPolicial').exists() and personal_policial is not None:
                        personal_policial.subcircuito = combined_form.cleaned_data.get('subcircuito')
                        personal_policial.save()

                    user.groups.clear()  # Elimina todas las asignaciones de grupo existentes
                    user.groups.add(*new_groups)  # Asigna los nuevos grupos
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
                    email=combined_form.cleaned_data.get('email'),
                    password=combined_form.cleaned_data.get('password'),
                    first_name=combined_form.cleaned_data.get('first_name'),
                    last_name=combined_form.cleaned_data.get('last_name')
                )
                usuario = combined_form.save(commit=False)                
                usuario.user = user
                usuario.tipo_sangre = combined_form.cleaned_data.get('tipo_sangre')  # Asegúrate de que se está manejando el campo 'tipo_sangre'
                usuario.save()
                logger.info('Usuario creado: %s', usuario)

                groups = combined_form.cleaned_data.get('rol')
                user.groups.add(*groups)  # Asigna los nuevos grupos

                if groups.filter(name='Encargados de logística').exists():
                    tecnico = Tecnico(usuario=usuario, titular=combined_form.cleaned_data.get('titular'))
                    tecnico.save()
                    logger.info('Tecnico creado: %s', tecnico)

                if groups.filter(name='Personal policial agentes').exists():   
                    personal_policial = PersonalPolicial(usuario=usuario, subcircuito=combined_form.cleaned_data.get('subcircuito'))
                    personal_policial.save()
                    logger.info('Personal policial creado: %s', personal_policial)
                messages.success(request, 'Usuario creado exitosamente')
                return redirect('admin:index')

        else:
            combined_form = CombinedForm()

        return render(request, 'admin/custom_add_form.html', {
            'combined_form': combined_form
        })
    

admin.site.register(Usuario, CombinedAdmin)
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
    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Subcircuitos, SubcircuitoAdmin)


class OrdendeTrabajoAdmin(admin.ModelAdmin):
    list_display = ('fecha','estado', 'tipo_orden', 'tecnico')    
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
    # Lista de campos a mostrar en la vista de lista
    list_display = ('marca', 'modelo', 'chasis', 'placa', 'kilometraje', 'subcircuito_cod', 'subcircuito_nombre')    
    # Método para mostrar el código del subcircuito 
    def subcircuito_cod(self, obj):
        return obj.subcircuito.cod_subcircuito   
    def subcircuito_nombre(self, obj):
        return obj.subcircuito.nombre_subcircuito    
    # Nombres personalizados para las columnas
    subcircuito_cod.short_description = 'Código Subcircuito'
    subcircuito_nombre.short_description = 'Nombre Subcircuito'

    class Media:
        js = ('static/js/admin_autocomplete.js',)

admin.site.register(FlotaVehicular, FlotaVehicularAdmin)


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
'''
    def reporte_link(self, obj):
        url = reverse('reporte_quejas_sugerencias')
        return format_html('<a href="{}">Generación de Reportes</a>', url)
    reporte_link.short_description = 'Reporte'
'''
'''    def reporte_link(self, obj):
        url = reverse('reporte_quejas_sugerencias_pdf')
        return format_html('<a href="{}">Ver Reporte PDF</a>', url)
    reporte_link.short_description = 'Reporte PDF'''
admin.site.register(QuejaSugerencia, QuejaSugerenciaAdmin)

