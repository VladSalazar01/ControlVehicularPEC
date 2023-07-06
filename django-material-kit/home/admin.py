from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path
from .models import *
from django.shortcuts import render, redirect
from .forms import CombinedForm
from django.contrib import messages


# Register your models here.

'''class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('tipo_sange','rango', 'datos_usuario')
    def datos_usuario(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
admin.site.register(Usuario, UsuarioAdmin)

#display tecnico
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ('nombre_tecnico','titular', 'rango')
    def nombre_tecnico(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def rango(self, obj):
        return f"{obj.usuario.rango} "    
admin.site.register(Tecnico, TecnicoAdmin)

admin.site.register(PersonalPolicial)'''

#---personalizacion de admin panel para agregar usuarios---
class CombinedAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add/', self.admin_site.admin_view(self.custom_add_view), name='custom-add'),
        ]
        return custom_urls + urls

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
                usuario.save()

                role = combined_form.cleaned_data.get('rol')
                if role == 'personal_policial':
                    PersonalPolicial.objects.create(
                        usuario=usuario,
                        subcircuito=combined_form.cleaned_data.get('subcircuito')
                    )                    
                    group = Group.objects.get(name="Personal policial agentes")
                    user.groups.add(group)
                elif role == 'tecnico':
                    Tecnico.objects.create(
                        usuario=usuario,
                        titular=combined_form.cleaned_data.get('titular')
                    )                    
                    group = Group.objects.get(name="Encargados de logística")
                    user.groups.add(group)
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
#admin.site.register(Subcircuitos)
#--fin personalizacion agregar  usuarios--

#display dependencia (actualizar metodos PND, solo si van a ser usados en list_display)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ('provincia','no_circuitos', 'parroquia')
    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Dependencia, DependenciaAdmin)

#display distrito (actualizar metodos PND, solo si van a ser usados en list_display)
class DistritoAdmin(admin.ModelAdmin):
    list_display = ('cod_Distrito','nombre_Distrito', 'no_Circuitos')
    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Distrito, DistritoAdmin)

#display circuito (actualizar metodos PND, solo si van a ser usados en list_display)
class CircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_Circuito','nombre_Circuito', 'no_Subcircuitos')
    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Circuito, CircuitoAdmin)

#display subcircuito (actualizar metodos PND, solo si van a ser usados en list_display)
class SubcircuitoAdmin(admin.ModelAdmin):
    list_display = ('cod_subcircuito','nombre_subcircuito')
    def PND(self, obj):
        return f"{obj.usuario.user.username} {obj.usuario.user.last_name}"
    def PND2(self, obj):
        return f"{obj.usuario.rango} "
admin.site.register(Subcircuitos, SubcircuitoAdmin)

admin.site.register(OrdendeTrabajo)
admin.site.register(OrdenMantenimiento)
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
admin.site.register(FlotaVehicular, FlotaVehicularAdmin)


admin.site.register(Mantenimientos)
