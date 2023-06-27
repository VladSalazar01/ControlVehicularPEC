from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
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
admin.site.register(PersonalPolicial)
admin.site.register(OrdendeTrabajo)
admin.site.register(OrdenMantenimiento)
admin.site.register(OrdenCombustible)
admin.site.register(PartePolicial)
admin.site.register(TallerMecanico)
admin.site.register(FlotaVehicular)
admin.site.register(Mantenimientos)
