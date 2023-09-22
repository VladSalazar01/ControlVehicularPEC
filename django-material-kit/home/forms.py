
from django import forms
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from .models import *
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib import admin
from tinymce.widgets import TinyMCE


#crear parte policial

class PartePolicialForm(forms.ModelForm):
    fecha_solicitud = forms.DateTimeField(
        label="Fecha de Mantenimiento:", 
        required=True, 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    observaciones = forms.CharField(widget=TinyMCE(attrs={'cols': 120, 'rows': 15}))
    estado = forms.CharField(initial='En Proceso', widget=forms.HiddenInput())  # campo oculto con valor predeterminado 'En Proceso'

    class Meta:
        model = PartePolicial
        fields = ['tipo_parte', 'observaciones', 'estado', 'fecha_solicitud', 'kilometraje_actual']  


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # acceder al usuario
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_solicitud = cleaned_data.get("fecha_solicitud")
        kilometraje_actual = cleaned_data.get("kilometraje_actual")
        tipo_parte = cleaned_data.get("tipo_parte")
        
        print("Valor de tipo_parte:", tipo_parte)

        personal_policial = PersonalPolicial.objects.get(usuario__user=self.user)
        flota_vehicular = personal_policial.flota_vehicular
        if not flota_vehicular:
            self.add_error(None, "El parte no se ha registrado porque no tiene ningún vehículo asociado.")

        if fecha_solicitud and fecha_solicitud <= timezone.now():
            self.add_error(None, "La fecha de mantenimiento debe ser una fecha futura.")

        if flota_vehicular and kilometraje_actual and kilometraje_actual <= flota_vehicular.kilometraje:
            self.add_error(None, "El kilometraje actual debe ser mayor al kilometraje del vehículo.")

class FinalizarOrdenForm(forms.Form):
    observaciones = forms.CharField(widget=forms.Textarea, required=False)

class OrdenMantenimientoForm(forms.ModelForm):
    class Meta:
        model = OrdenMantenimiento
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        if field_name == 'fecha':
            return timezone.now()
        return super().get_initial_for_field(field, field_name)
    
    def clean(self):
        cleaned_data = super().clean()
        tipos_mantenimiento = cleaned_data.get('tipos_mantenimiento')
        if tipos_mantenimiento is not None:
            tipos_mantenimiento = [tipo.tipo for tipo in tipos_mantenimiento]
            if 'M1' in tipos_mantenimiento and 'M2' in tipos_mantenimiento:
                raise ValidationError("No se puede seleccionar 'Mantenimiento 1' y 'Mantenimiento 2' al mismo tiempo.")
        return cleaned_data
    
class TipoMantenimientoForm(forms.ModelForm):
    class Meta:
        model = OrdenMantenimiento
        fields = ['tipos_mantenimiento']


'''    
    def clean_tipo_mantenimiento(self):
        tipo_mantenimiento = self.cleaned_data.get('tipo_mantenimiento')
        if 'M1' in tipo_mantenimiento and 'M2' in tipo_mantenimiento:
            raise forms.ValidationError('No puede seleccionar "Mantenimiento 1" y "Mantenimiento 2" a la vez.')
        return tipo_mantenimiento
''' 
#crear usuario----


#buzon de quejas form
class QuejaSugerenciaForm(forms.ModelForm):
    class Meta:
        model = QuejaSugerencia
        fields = ['circuito', 'subcircuito', 'tipo', 'detalles', 'contacto', 'nombres', 'apellidos']

#orden de movilizacion
class OrdenMovilizacionForm(forms.ModelForm):
    class Meta:
        model = OrdenMovilizacion
        exclude = ['personal_policial_solicitante', 'numero_ocupantes', 'ocupantes'] 
        fields = [
            'motivo',
            'fecha_salida',
            'hora_salida',
            'ruta',
            'kilometraje_inicio',
            'personal_policial_solicitante',
            'conductor',
            'vehiculo',
            'numero_ocupantes',
            'ocupantes',  
        ]
        widgets = {
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
            'personal_policial_solicitante': forms.Select(attrs={'class': 'form-control'}),
            'conductor': forms.Select(attrs={'class': 'form-control'}),
            'vehiculo': forms.Select(attrs={'class': 'form-control'}),
            'ocupantes': forms.SelectMultiple(attrs={'class': 'form-control'}),  
                            }

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        if 'personal_policial_solicitante' in self.fields:
            self.fields['personal_policial_solicitante'].queryset = PersonalPolicial.objects.all()

        self.fields['conductor'].queryset = PersonalPolicial.objects.all()
        self.fields['vehiculo'].queryset = FlotaVehicular.objects.all()
       

    def clean(self):
        cleaned_data = super().clean()
        
    def clean_kilometraje_inicio(self):
        kilometraje = self.cleaned_data.get('kilometraje_inicio')
        if kilometraje < 0:
            raise ValidationError('El kilometraje de inicio no puede ser negativo.')
        return kilometraje

    def clean_numero_ocupantes(self):
        num_ocupantes = self.cleaned_data.get('numero_ocupantes')
        if num_ocupantes < 0:
            raise ValidationError('El número de ocupantes no puede ser negativo.')
        return num_ocupantes
    
    

class NumeroOcupantesForm(forms.Form):
    numero_ocupantes = forms.IntegerField(min_value=1, label='Número de Ocupantes')


class SeleccionarOcupantesForm(forms.Form):
    ocupantes = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, max_ocupantes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_ocupantes = max_ocupantes
        self.fields['ocupantes'].queryset = Ocupante.objects.all()
    def clean_ocupantes(self):
        ocupantes = self.cleaned_data.get('ocupantes')
        if len(ocupantes) > self.max_ocupantes:
            raise forms.ValidationError(f'No puedes seleccionar más de {self.max_ocupantes} ocupantes.')
        return ocupantes


