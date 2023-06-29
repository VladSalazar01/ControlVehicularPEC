from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
#para validaciones (cedula)
from django.core.exceptions import ValidationError

#modelos para la expansion de auth.user
class Usuario(models.Model): # usar para extension de aut.user       
    #rol = models.CharField(max_length=45, null=True)       [usar para solo lectura]     
    direccion = models.CharField(max_length=45, null=True,blank=True)
    fecha_de_nacimiento = models.DateField(null=True,blank=True)
    GENEROop=   [('M','Masculino'),
                ('F','Femenino'), ]
    genero = models.CharField(db_column='Genero', max_length=1, blank=True, null=True, choices=GENEROop)
    identificacion = models.CharField(
                                    max_length=50, db_column='Identificacion',
                                    null=True, blank=False
                                    )    
    rnks = [
            ('Pol', 'Policía'),
            ('CS', 'Cabo Segundo'),
            ('CP', 'Cabo Primero'),
            ('SaS', 'Sargento Segundo'),
            ('SaP', 'Sargento Primero'),
            ('SoS', 'Suboficial Segundo'),
            ('SoP', 'Suboficial Primero'),
            
            ('ST', 'Subteniente'),
            ('Te', 'Teniente'),
            ('CaP', 'Capitán'),
            ('MaY', 'Mayor'),
            ('TeC', 'Teniente Coronel'),           
             ]
    rango = models.CharField(db_column='Rango', blank=True, null=True, choices=rnks, max_length=3)
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
    tipo_sange = models.CharField(db_column='Tipo de sangre', blank=True, null=True, choices=tds, max_length=3)     
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='usuario', blank=True, null=True)#foranea one to one de user CASCADE

    def __str__(self):
            return f"{self.user.first_name} {self.user.last_name}"
    class Meta:
        db_table = 'Usuario datos'
        verbose_name_plural='Datos de usuario'
        
       

class Tecnico(models.Model):   
    titular = models.BooleanField() #titular /auxiliar usar unicamente si se justifica
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING)   
    def __str__(self):
            return f"{self.usuario.user.first_name} {self.usuario.user.last_name}"
    class Meta:
        db_table = 'Tecnico'
        verbose_name_plural='Encargados de logística'
        
       
#class personalPolicial(): está en otro trio
#--fin modelos para la expansion de auth.user--

#Administracion de dependencias
class Dependencia(models.Model):  
    sel_provincia = [
            ('Loja', 'Loja'),  
            ('otr', 'otra..'),          
             ]
    provincia = models.CharField(db_column='Provincia', blank=True, null=True, choices=sel_provincia, max_length=26)
    no_circuitos = models.CharField(max_length=45, null=True)
    sel_parroquia= [
            ('VILCABAMBA', 'VILCABAMBA(VICTORIA)'),  
            ('QUINARA','(QUINARA)'), 
            ('MALACATOS','MALACATOS(VALLADOLID)'),
            ('CHUQUIRIBAMBA','(CHUQUIRIBAMBA)'),
            ('TAQUIL','TAQUIL(MIGUEL RIOFRIO)'),
            ('Loja','LOJA(LOJA)'),
             ]
    parroquia = models.CharField(db_column='Parroqia', blank=True, null=True, choices=sel_parroquia, max_length=26)
    def __str__(self):
            return f"{self.provincia}, {self.parroquia}"
    class Meta:
        db_table = 'Dependencia'
        verbose_name_plural='Dependencias'

class Distrito(models.Model):    
    cod_Distrito = models.CharField(max_length=45, null=True)# necesita ser único
    nombre_Distrito = models.CharField(max_length=45, null=True)
    no_Circuitos = models.IntegerField(null=True)
    distritoDependencia = models.ForeignKey(Dependencia, on_delete=models.DO_NOTHING, db_column='idDependencia')
    def __str__(self):
        return f"{self.cod_Distrito}, {self.nombre_Distrito}"
    class Meta:
        db_table = 'Distrito' 
        verbose_name_plural='Distritos'  

class Circuito(models.Model):   
    cod_Circuito = models.CharField(max_length=45, null=True)
    nombre_Circuito = models.CharField(max_length=45, null=True)
    no_Subcircuitos = models.IntegerField(null=True)
    circuitoDistrito = models.ForeignKey(Distrito, on_delete=models.DO_NOTHING, db_column='Distrito_id')
    def __str__(self):
            return f"{self.cod_Circuito}, {self.nombre_Circuito}"
    class Meta:
        db_table = 'Circuito' 
        verbose_name_plural='Circuitos'  

class Subcircuitos(models.Model):
    cod_subcircuito = models.CharField(max_length=45, blank=True, null=True)
    nombre_subcircuito = models.CharField(max_length=45, blank=True, null=True)
    subcircuitoCircuito = models.ForeignKey(Circuito, models.DO_NOTHING, db_column='Circuito_idCircuito')
    def __str__(self):
        return f"{self.cod_subcircuito}, {self.nombre_subcircuito}"
    class Meta:
        db_table = 'Subcircuitos'
        verbose_name_plural='Subcircuitos'
#fin de admin subcircuito---

class PersonalPolicial(models.Model):         
    subcircuito = models.ForeignKey(Subcircuitos, models.DO_NOTHING, related_name='PersonalPolicial_Subcircuito')#foranea asignacion    
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='usuario_UsuarioID', null=True,blank=True)#foranea user
    subcircuito = models.ForeignKey(Subcircuitos, on_delete=models.DO_NOTHING)#foranea subcircuito

    class Meta:
        db_table = 'Personal Policial' 
        verbose_name_plural='Personal Policial'
  
#3trio problemas con los nombres de atributos, muy larcos mucho sub-gion

class OrdendeTrabajo(models.Model):     
    fecha = models.DateField(null=True)
    sel_estado = [
            ('Activa', 'Orden activa'),  
            ('Despachada','Orden despachada'),             
             ]
    estado = models.CharField(db_column='Estado de Orden', blank=True, null=True, choices=sel_estado, max_length=26)
    sel_torden= [
            ('Mantenimiento', 'Orden de Mantenimiento'),  
            ('Combsustible','Orden de combustible'),             
             ]
    tipo_orden = models.CharField(db_column='Tipo de orden', blank=True, null=True, choices=sel_torden, max_length=26)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.DO_NOTHING)#foranea tipo de orden

    class Meta:
       db_table = 'Ordenes de Trabajo' 
       verbose_name_plural='Ordenes de trabajo'

class OrdenMantenimiento(models.Model):
    sel_tmantenimiento= [
            ('M1', 'Mantenimiento tipo 01'),  
            ('M2', 'Mantenimiento tipo 02'),             
            ('M3', 'Mantenimiento tipo 03')
             ]        
    tipo_mantenimiento = models.CharField(db_column='Tipo de Mantenimiento', blank=True, null=True, choices=sel_tmantenimiento, max_length=26)
    ordende_trabajo = models.ForeignKey(OrdendeTrabajo, on_delete=models.DO_NOTHING)#foranea tipo de orden

    class Meta:
       db_table = 'Ordenes de Mantenimiento'
       verbose_name_plural='Ordenes de Mantenimiento'

class OrdenCombustible(models.Model): 
    sel_tcombustible= [
            ('Diesel','Combustible Diesel'),  
            ('Extra','Combustible Extra'),  
            ('Super','Combustible Super'),            
             ]  
    tipo_de_combustible = models.CharField(db_column='Tipo de combustible', blank=True, null=True, choices=sel_tcombustible, max_length=26)   
    cantidad_galones = models.CharField(max_length=45, null=True)
    cantidad_galones_detalle = models.CharField(max_length=45, null=True)    
    ordende_trabajo = models.ForeignKey(OrdendeTrabajo, on_delete=models.DO_NOTHING)#foranea tipo de orden

    class Meta:
       db_table = 'Ordenes de Combustible'
       verbose_name_plural='Ordenes de Combustible'

#4trio 
class PartePolicial(models.Model):    
    fecha = models.DateField(max_length=45, blank=True, null=True)
    sel_tparte= [
            ('Mantenimiento Preventivo','Mantenimiento preventivo'),  
            ('Mantenimiento emergente','Mantenimiento emergente'),  
            ('Novedades','Novedades'),            
             ] 
    tipo_parte = models.CharField(db_column='Tipo de Parte', blank=True, null=True, choices=sel_tparte, max_length=26)   
    observaciones = models.TextField(max_length=450, blank=True, null=True)
    personalPolicial = models.ForeignKey(PersonalPolicial, models.DO_NOTHING,)
    
    class Meta:
        db_table = 'Parte Policial'
        verbose_name_plural='Partes Policiales'

#5trio ultimo
class TallerMecanico(models.Model):    
    mecanico_responsable = models.CharField(max_length=45, null=True)
    nombre = models.CharField(max_length=45, null=True)
    direccion = models.TextField(max_length=45, null=True)
    telefono = models.CharField(max_length=45, null=True)
    sel_ttaller= [
            ('Institucional','Taller institucional'),  
            ('Particular','Taller particular'),                      
             ] 
    tipo_taller = models.CharField(db_column='Tipo de taller', blank=True, null=True, choices=sel_ttaller, max_length=26)   

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
    marca = models.CharField(max_length=45, null=True)
    modelo = models.CharField(max_length=45, null=True)
    motor = models.CharField(db_column='Motor Marca', max_length=45, null=True)
    kilometraje = models.IntegerField(null=True)
    cilindraje = models.CharField(max_length=45, null=True)
    capacidad_de_carga = models.CharField(max_length=45, null=True)
    capacidad_de_pasajeros = models.IntegerField(null=True)
    subcircuito = models.ForeignKey(Subcircuitos, on_delete=models.DO_NOTHING)#foranea subcircuito

    class Meta:
        db_table = 'Flota Vehicular'
        verbose_name_plural='Flota vehicular'

class Mantenimientos(models.Model):     
    taller = models.ForeignKey(TallerMecanico, on_delete=models.DO_NOTHING)#foranea taller   
    orden_mantenimiento = models.ForeignKey(OrdenMantenimiento, on_delete=models.DO_NOTHING)#foranea ordende trabajo
    vehiculo = models.ForeignKey(FlotaVehicular, on_delete=models.DO_NOTHING)#foranea vehiculo

    class Meta:
        db_table = 'Mantenimiento'
        verbose_name_plural='Mantenimientos'
   
  


