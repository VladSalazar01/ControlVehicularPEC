from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
import requests
from django.core.validators import RegexValidator
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator


class UserProxy(User):
    class Meta:
        proxy = True    
        db_table = 'Usuarios_primario'
        verbose_name ='Usuario'
        verbose_name_plural='Datos de Usuario'    
#clase abstracta para el borrado suave
class GroupProxy(Group):
    class Meta:
        proxy = True
        db_table = 'Roles_grupos'
        verbose_name ='Rol+'
        verbose_name_plural='Roles'  

class SoftDeletionModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    def delete(self):
        self.is_deleted = True
        self.save()
    class Meta:
        abstract = True

##----catálogos----
def get_vehicle_data(make, year):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"
    response = requests.get(url)
    data = response.json()
    return data['Results'] if data['Count'] > 0 else []

class Rango_ctlg(models.Model):  
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.nombre}"
    class Meta:
        db_table = 'Rango' 
        verbose_name_plural='Rangos'  
    
##fin catalogos----



#proximodel roles y permisos
class CustomPermission(Permission):
    class Meta:
        proxy = True

    def __str__(self):
        # Cambia cómo se muestra el nombre del permiso
        name = super().__str__()
        name = name.replace('group', 'rol')
        name = name.replace('Can add group', _('Puede agregar rol'))
        return name
     
#modelos para la expansion de auth.user
class Usuario(SoftDeletionModel, models.Model):   
    is_deleted = models.BooleanField(default=False)
    direccion = models.TextField(max_length=810, null=True, blank=True)
    fecha_de_nacimiento = models.DateField(null=True,blank=True)
    GENEROop=   [('M','Masculino'),
                ('F','Femenino'), ]
    genero = models.CharField(db_column='Genero', max_length=1, blank=True, null=True, choices=GENEROop)
    identificacion_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="La identificación debe ser exactamente 10 dígitos."
    )
    identificacion = models.CharField(
        max_length=50,
        db_column='Identificacion',
        null=True,
        blank=False,
        validators=[identificacion_validator]
    )       
    rango = models.ForeignKey(Rango_ctlg, on_delete=models.SET_NULL, null=True, blank=True)
    tds=   [
            ('A+', 'A positivo'),
            ('A-', 'A negativo'),
            ('B+', 'B positivo'),
            ('B-', 'B negativo'),
            ('AB+', 'AB positivo'),
            ('AB-', 'AB negativo'),
            ('O+', 'O positivo'),
            ('O-', 'O negativo'),
             ]
    tipo_sangre = models.CharField(db_column='Tipo de sangre', blank=True, null=True, choices=tds, max_length=3)     
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='usuario', blank=True, null=True)#foranea one to one de user CASCADE

    def __str__(self):
            return f"{self.user.first_name}-{self.user.last_name}"
    class Meta:
        db_table = 'Usuario datos'
        verbose_name_plural='Datos de usuario'
        
class Tecnico(SoftDeletionModel, models.Model):   
    is_deleted = models.BooleanField(default=False)
    titular = models.BooleanField(blank=True, null=True) #titular /auxiliar usar unicamente si se justifica
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)   
    def __str__(self):
            return f"{self.usuario.user.first_name}-{self.usuario.user.last_name}"
    class Meta:
        db_table = 'Tecnico'
        verbose_name_plural='Encargados de logística'
        
       
#class personalPolicial(): está en otro trio
#--fin modelos para la expansion de auth.user--

#Administracion de dependencias
class Provincia(models.Model):    
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nombre}"
    class Meta:
        db_table = 'Provincia' 
        verbose_name_plural='Provincias'  

class Parroquia(models.Model):    
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='parroquias')
    def __str__(self):
        return f"{self.provincia},{self.nombre}"
    class Meta:
        db_table = 'Parroquia' 
        verbose_name_plural='Parroquias'  

class Distrito(models.Model):    
    cod_Distrito = models.CharField(max_length=45, unique=True, blank=True)# necesita ser único
    nombre_Distrito = models.CharField(max_length=45, null=True)    
    provincia = models.ForeignKey(Provincia, on_delete=models.DO_NOTHING, related_name='distritos')
    def __str__(self):
        return f"{self.cod_Distrito}, {self.nombre_Distrito}"
    class Meta:
        db_table = 'Distrito' 
        verbose_name_plural='Distritos'  

class Circuito(models.Model):   
    cod_Circuito = models.CharField(max_length=10, unique=True, blank=True)
    nombre_Circuito = models.CharField(max_length=45, null=True)   
    circuitoDistrito = models.ForeignKey(Distrito, on_delete=models.CASCADE,related_name='circuito', db_column='Distrito_id')
    def __str__(self):
            return f"{self.cod_Circuito}, {self.nombre_Circuito}"
    class Meta:
        db_table = 'Circuito' 
        verbose_name_plural='Circuitos'  

class Subcircuitos(models.Model):
    cod_subcircuito = models.CharField(max_length=45, unique=True, blank=True)
    nombre_subcircuito = models.CharField(max_length=45, blank=True, null=True)
    subcircuitoCircuito = models.ForeignKey(Circuito, on_delete=models.CASCADE, related_name='subcircuito',db_column='Circuito_idCircuito')
    parroquia = models.ForeignKey(Parroquia, on_delete=models.DO_NOTHING, related_name='subcircuitos')
    def __str__(self):
        return f"{self.cod_subcircuito}, {self.nombre_subcircuito}"
    class Meta:
        db_table = 'Subcircuitos'
        verbose_name_plural='Subcircuitos'


class PersonalPolicial(SoftDeletionModel, models.Model): 
    is_deleted = models.BooleanField(default=False)        
    usuario = models.OneToOneField(Usuario, models.CASCADE, db_column='usuario_UsuarioID', null=True,blank=True)#foranea user
    flota_vehicular = models.ForeignKey('FlotaVehicular', on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_policial') 
    turno_inicio = models.TimeField(null=True, blank=True)
    turno_fin = models.TimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    subcircuito = models.ForeignKey('Subcircuitos', on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_policial') 
    def clean(self):
        super().clean()  
        if self.flota_vehicular:
            personal_policial_mismo_vehiculo = PersonalPolicial.objects.filter(flota_vehicular=self.flota_vehicular).exclude(id=self.id)
            for otro_personal in personal_policial_mismo_vehiculo:
                if otro_personal.turno_inicio is not None and otro_personal.turno_fin is not None and self.turno_inicio is not None and self.turno_fin is not None:
                    if (otro_personal.turno_inicio <= self.turno_fin and otro_personal.turno_fin >= self.turno_inicio):
                        raise ValidationError(f"El turno se superpone con el de {otro_personal}.")
    def __str__(self):
        return f"{self.usuario.user.first_name} ; {self.usuario.user.last_name}"
    class Meta:
        db_table = 'Personal Policial' 
        verbose_name_plural='Personal Policial'
 

class OrdendeTrabajo(models.Model):     
    fecha = models.DateTimeField(null =True, auto_now_add=True, editable=False)
    fecha_de_entrega = models.DateTimeField(null=True, blank=True, editable=False)
    creador = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)s_creadas')
    aprobador = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)s_aprobadas')
    sel_estado = [
        ('Activa', 'Orden activa'),  
        ('Despachada','Orden despachada'),             
    ]
    estado = models.CharField(db_column='Estado de Orden', blank=True, null=True, choices=sel_estado, max_length=26)

    class Meta:
        abstract = True
    
class TipoMantenimiento(models.Model):
    sel_tmantenimiento= [
        ('M1', 'Mantenimiento tipo 01'),  
        ('M2', 'Mantenimiento tipo 02'),             
        ('M3', 'Mantenimiento tipo 03')
    ]   
    tipo = models.CharField(max_length=2, choices=sel_tmantenimiento)
    descripcion = models.TextField(blank=True)
    costo = models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self):
        return self.get_tipo_display()
   
class OrdenCombustible(OrdendeTrabajo): 
    sel_tcombustible= [
        ('Diesel','Combustible Diesel'),  
        ('Extra','Combustible Extra'),  
        ('Super','Combustible Super'),            
    ]  
    tipo_de_combustible = models.CharField(db_column='Tipo de combustible', blank=True, null=True, choices=sel_tcombustible, max_length=26)   
    cantidad_galones = models.CharField(max_length=45, null=True)
    cantidad_galones_detalle = models.CharField(max_length=45, null=True)

    '''
    creador = models.ForeignKey(User, related_name='ordenes_combustible_creadas', on_delete=models.DO_NOTHING, null=True, blank=True)
    aprobador = models.ForeignKey(User, related_name='ordenes_combustible_aprobadas', on_delete=models.DO_NOTHING, null=True, blank=True)
    '''

    def __str__(self):
            return f"{self.fecha} - {self.tipo_de_combustible} - {self.cantidad_galones_detalle}"
    class Meta:
        db_table = 'Ordenes de Combustible'
        verbose_name_plural='Ordenes de Combustible'
#4trio 
class PartePolicial(models.Model):    
    fecha = models.DateTimeField(max_length=45, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(null=True, blank=True)  
    kilometraje_actual = models.IntegerField(null=True, blank=True)  
    sel_tparte= [
        ('Mantenimiento Preventivo','Mantenimiento preventivo'),  
        ('Mantenimiento Correctivo','Mantenimiento correctivo'),  
        ('Solicitud de Combustible','Solicitud de combustible'),  
        ('Novedades','Novedades'),            
    ]  
    tipo_parte = models.CharField(db_column='Tipo de Parte', blank=True, null=True, choices=sel_tparte, max_length=26)   
    observaciones = models.TextField(max_length=450, blank=True, null=True)
    ESTADOS = [
        ('En Proceso', 'En Proceso'),
        ('Completado', 'Completado'),
        ('Rechazado', 'Rechazado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='En Proceso')
    personalPolicial = models.ForeignKey(PersonalPolicial, models.DO_NOTHING,)
    
    def __str__(self):
        return f"El parte {self.tipo_parte}, con fecha {self.fecha},"
    class Meta:
        db_table = 'Parte Policial'
        verbose_name_plural='Partes Policiales'

class OrdenMantenimiento(OrdendeTrabajo):
    tipos_mantenimiento = models.ManyToManyField(TipoMantenimiento, blank=True)
    parte_asociado = models.FileField(upload_to='partes_asociados/', null=True, blank=False, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpeg', 'png'])])
    asunto = models.CharField(max_length=255, null=True, blank=True)
    detalle = models.TextField(null=True, blank=True) 

    kilometraje_actual = models.IntegerField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)  
    parte_policial = models.ForeignKey(PartePolicial, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_mantenimiento')
       
    def __str__(self):
        return f"{self.fecha}"
    class Meta:
        db_table = 'Ordenes de Mantenimiento'
        verbose_name_plural='Ordenes de Mantenimiento'

#5trio ultimo
class TallerMecanico(models.Model):    
    mecanico_responsable = models.CharField(max_length=45, null=True)
    nombre = models.CharField(max_length=45, null=True, blank=True)
    direccion = models.TextField(max_length=600, null=True, blank=True)
    telefono = models.CharField(max_length=45, null=True, blank=True)
    sel_ttaller= [
            ('Institucional','Taller institucional'),  
            ('Particular','Taller particular'),                      
             ] 
    tipo_taller = models.CharField(db_column='Tipo de taller', blank=True, null=True, choices=sel_ttaller, max_length=26)   
    def __str__(self):
        return f"{self.nombre},{self.tipo_taller},"
    class Meta:
        db_table = 'Taller mecanico'
        verbose_name_plural='Talleres Mecánicos'

class FlotaVehicular(models.Model):       
    sel_tvehiculo= [
            ('Auto','Automóvil'),  
            ('Moto','Motocicleta'),  
            ('Camioneta','Camioneta'),            
            ]     
    tipo_vehiculo = models.CharField(db_column='Tipo de Vehículo', blank=True, null=True, choices=sel_tvehiculo, max_length=26)   
    placa = models.CharField(max_length=45, null=True)
    chasis = models.CharField(max_length=45, null=True)
    año = models.IntegerField(null=True, blank=True)
    marca = models.CharField(max_length=45, null=True)
    modelo = models.CharField(max_length=45, null=True)
    motor = models.CharField(db_column='Motor Marca', max_length=45, null=True)
    kilometraje = models.IntegerField(null=True)
    cilindraje = models.CharField(max_length=45, null=True)
    capacidad_de_carga = models.CharField(max_length=45, null=True)
    capacidad_de_pasajeros = models.IntegerField(null=True)
    subcircuito = models.ForeignKey(Subcircuitos, on_delete=models.DO_NOTHING , related_name='flota_vehicular',null=True, blank=True,)
    def __str__(self):
        return f"{self.marca},{self.modelo},{self.placa}"
    def clean(self):     
        from django.core.exceptions import ValidationError      
        if self.pk is not None:  # Solo realizar esta validación si el objeto ya ha sido guardado
            personal_policial_count = self.personal_policial.count()
            if personal_policial_count < 1 or personal_policial_count > 4:
                raise ValidationError('Un vehículo debe tener entre 1 y 4 Personal Policial asignados.')
    class Meta:
        db_table = 'Flota Vehicular'
        verbose_name_plural='Vehículos'

class Mantenimientos(models.Model):     
    taller = models.ForeignKey(TallerMecanico, on_delete=models.DO_NOTHING)#foranea taller   
    orden_mantenimiento = models.ForeignKey(OrdenMantenimiento, on_delete=models.DO_NOTHING)#foranea ordende trabajo
    vehiculo = models.ForeignKey(FlotaVehicular, on_delete=models.DO_NOTHING)#foranea vehiculo

    class Meta:
        db_table = 'Mantenimiento'
        verbose_name_plural='Mantenimientos'
   
##EVALUACIÓN buzon de quejas---
class QuejaSugerencia(models.Model):
    TIPO_CHOICES = [
        ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'),
    ]
    circuito = models.ForeignKey(Circuito, on_delete=models.DO_NOTHING)
    subcircuito = models.ForeignKey(Subcircuitos, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    detalles = models.TextField()
    contacto = models.CharField(max_length=100, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)   
    fecha_creacion = models.DateTimeField(auto_now_add=True)
##fin evaluacion buzon de quejas----  

#evaluacion orden de movilizavcion

class Ocupante(models.Model):
    nombre = models.CharField(max_length=100)
    datos = models.TextField(max_length=530)
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ocupante"
        verbose_name_plural = "Ocupantes"

class OrdenMovilizacion(models.Model):
    motivo = models.CharField(max_length=200)
    fecha_salida = models.DateField()
    hora_salida = models.TimeField()
    ruta = models.CharField(max_length=200)
    kilometraje_inicio = models.IntegerField()
    ESTADOS = (
    ('Pendiente', 'Pendiente'),
    ('Aprobado', 'Aprobado'),
    ('Rechazado', 'Rechazado'),)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    aprobador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    personal_policial_solicitante = models.ForeignKey(PersonalPolicial, related_name='ordenes_movilizacion', on_delete=models.CASCADE)
    conductor = models.ForeignKey(PersonalPolicial, related_name='ordenes_como_conductor', on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(FlotaVehicular, related_name='ordenes_movilizacion', on_delete=models.CASCADE)

    numero_ocupantes = models.IntegerField(default=0)
    fecha_solicitud = models.DateField(auto_now_add=True)

    ocupantes = models.ManyToManyField(Ocupante)

    def nombre_dependencia(self):
        return self.personal_policial_solicitante.subcircuito.nombre_subcircuito

    def nombre_completo_conductor(self):
        usuario_conductor = self.conductor.usuario
        user_conductor = usuario_conductor.user
        return f"{user_conductor.first_name} {user_conductor.last_name}"

    def nombre_completo_solicitante(self):
        usuario_solicitante = self.personal_policial_solicitante.usuario
        user_solicitante = usuario_solicitante.user
        return f"{user_solicitante.first_name} {user_solicitante.last_name}"

    def placa_vehiculo(self):
        return self.vehiculo.placa

    def marca_vehiculo(self):
        return self.vehiculo.marca
    def nombres_ocupantes(self):
        ocupantes = self.ocupantes.all()
        return ",\n".join([ocupante.nombre for ocupante in ocupantes])
    
    class Meta:
        verbose_name = "Orden de movilización"
        verbose_name_plural = "Ordenes de movilización"

#fin orden de movilizacion