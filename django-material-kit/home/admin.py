from django.contrib import admin
from django.contrib.auth.models import User
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
                elif role == 'tecnico':
                    Tecnico.objects.create(
                        usuario=usuario,
                        titular=combined_form.cleaned_data.get('titular')
                    )

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
admin.site.register(PartePolicial)
admin.site.register(TallerMecanico)
admin.site.register(FlotaVehicular)
admin.site.register(Mantenimientos)
