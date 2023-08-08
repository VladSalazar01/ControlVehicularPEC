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


@admin.register(OrdenMantenimiento)
class OrdenMantenimientoAdmin(admin.ModelAdmin):
    change_form_template = 'admin/orden_trabajo/ordenmantenimiento_change_form.html'
    change_list_template = 'admin/orden_trabajo/ordenmantenimiento_change_list.html'

    search_fields = ['fecha', 'tipos_mantenimiento__tipo', 'creador__username', 'aprobador__username', 'estado']

    list_filter = ['fecha', 'tipos_mantenimiento', 'creador', 'aprobador']
    list_display = ('fecha', 'get_tipo_mantenimiento', 'estado', 'creador', 'aprobador')
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create/', self.create_ordenmantenimiento, name='create_ordenmantenimiento'),
            path('<int:ordenmantenimiento_id>/update/', self.update_ordenmantenimiento, name='update_ordenmantenimiento'),
        ]
        return custom_urls + urls

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
    list_display = ('fecha', 'tipo_parte', 'observaciones', 'estado', 'nombre_personal_policial')
    readonly_fields = ['personalPolicial', 'fecha']
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

class SubcircuitoForm(forms.Form):
    subcircuito = forms.ModelChoiceField(queryset=Subcircuitos.objects.all())
class PersonalPolicialAdmin(admin.ModelAdmin):
    list_display = ['usuario',  'flota_vehicular', 'turno_inicio', 'turno_fin','subcircuito',]
    list_filter = ['usuario', 'flota_vehicular', 'subcircuito']
    #list_editable = ('subcircuito',)
    actions = ['asignar_subcircuito']
   
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

