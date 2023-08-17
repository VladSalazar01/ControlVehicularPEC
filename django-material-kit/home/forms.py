
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
'''
class PartePolicialForm(forms.ModelForm):
    tipo_parte = forms.ChoiceField(choices=PartePolicial.sel_tparte, widget=forms.Select(attrs={'id': 'tipo_parte'}))
    fecha_solicitud = forms.DateTimeField(label="Fecha de Mantenimiento:", required=True)
    estado = forms.CharField(initial='En Proceso', widget=forms.HiddenInput())  # campo oculto con valor predeterminado 'En Proceso'

    class Meta:
        model = PartePolicial
        exclude = ['fecha']  # excluimos la fecha del formulario
'''

class PartePolicialForm(forms.ModelForm):
    fecha_solicitud = forms.DateTimeField(
        label="Fecha de Mantenimiento:", 
        required=True, 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    #observaciones = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':15}),)
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

        personal_policial = PersonalPolicial.objects.get(usuario__user=self.user)
        flota_vehicular = personal_policial.flota_vehicular
        if not flota_vehicular:
            self.add_error(None, "El parte no se ha registrado porque no tiene ningún vehículo asociado.")

        if fecha_solicitud and fecha_solicitud <= timezone.now():
            self.add_error(None, "La fecha de mantenimiento debe ser una fecha futura.")

        if flota_vehicular and kilometraje_actual and kilometraje_actual <= flota_vehicular.kilometraje:
            self.add_error(None, "El kilometraje actual debe ser mayor al kilometraje del vehículo.")

'''
class OrdenMantenimientoForm(forms.ModelForm):
    class Meta:
        model = OrdenMantenimiento
        exclude = ['tipos_mantenimiento']
   
class TipoMantenimientoInlineFormset(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        mantenimientos_list = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE'):  # Ignore forms that will be deleted
                mantenimiento = form.cleaned_data.get('tipo_mantenimiento')
                if mantenimiento:
                    mantenimientos_list.append(mantenimiento.tipo)
        
        if 'M1' in mantenimientos_list and 'M2' in mantenimientos_list:
            raise ValidationError("No puedes elegir Mantenimiento 1 y Mantenimiento 2 al mismo tiempo.")

class TipoMantenimientoInline(admin.TabularInline):
    model = OrdenMantenimiento.tipos_mantenimiento.through
    extra = 1
    formset = TipoMantenimientoInlineFormset
'''
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
'''
class CombinedForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombres')
    last_name = forms.CharField(max_length=30, required=True, label='Apellidos')
    username = forms.CharField(max_length=30, required=True, label='Nombre de usuario')
    email = forms.EmailField(required=True, label='Correo electrónico')
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text='Ingrese una contraseña. Mínimo 8 caracteres.',
        validators=[MinLengthValidator(8)]
    )   
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text='Confirme su contraseña.',
        validators=[MinLengthValidator(8)]
    )
    
    direccion = forms.CharField(widget=forms.Textarea(attrs={'maxlength': 200}), required=False, label='Dirección')
    fecha_de_nacimiento = forms.DateField(
        widget=forms.SelectDateWidget(years=range(date.today().year - 100, date.today().year - 18)),
        required=False,
        label='Fecha de nacimiento'
    )
    identificacion = forms.CharField(
        max_length=10,
        error_messages={
            'max_length': 'La identificación debe tener exactamente 10 dígitos.',
            'required': 'Este campo es obligatorio.'
        },
        help_text='Ingrese un número de identificación de 10 dígitos.',
        validators=[RegexValidator(r'^\d{10}$', 'Identificación solo adminte números')]
    )    
    titular = forms.BooleanField(required=False,label='Titular')
    flota_vehicular = forms.ModelChoiceField(
        queryset=FlotaVehicular.objects.all(),
        required=False,
        label='Flota Vehicular',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    turno_inicio = forms.TimeField(
        required=False,
        label='Inicio de Turno',
        widget=forms.TimeInput(attrs={'class': 'form-control'})
    )
    turno_fin = forms.TimeField(
        required=False,
        label='Fin de Turno',
        widget=forms.TimeInput(attrs={'class': 'form-control'})
    )

    tipo_sangre = forms.ChoiceField(
        choices=Usuario.tds, 
        required=False, 
        label='Tipo de sangre',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rango = forms.ModelChoiceField(queryset=Rango_ctlg.objects.all(), required=False)  
    rol = forms.ModelMultipleChoiceField(queryset=Group.objects.all())
    class Meta:
        model = Usuario
        fields = ['direccion', 'fecha_de_nacimiento', 'genero', 'identificacion', 'rango', 'tipo_sangre']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if self.instance.id is not None:  # Estamos en el proceso de edición
            return identificacion
        else:  # Estamos en el proceso de creación
            if Usuario.objects.filter(identificacion=identificacion).exists():
                raise forms.ValidationError("La identificación ya está en uso.")
            return identificacion
    
    def __init__(self, *args, user_instance=None, tecnico_instance=None, personal_policial_instance=None,  group_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_instance:
            self.fields['username'].initial = user_instance.username
            self.fields['email'].initial = user_instance.email
            self.fields['password'].initial = user_instance.password
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
        if group_instance:
            self.fields['rol'].initial = group_instance.values_list('id', flat=True)
        if tecnico_instance:
            self.fields['titular'].initial = tecnico_instance.titular
        if personal_policial_instance:
            self.fields['flota_vehicular'].initial = personal_policial_instance.flota_vehicular

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        if 'identificacion' in exclude:
            exclude.remove('identificacion')  # No incluir 'identificacion' en la validación de unicidad

        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            self._update_errors(e)
'''

#----ordenes de trabajo formclass OrdenTrabajoForm(forms.ModelForm):---DEPRECAR

'''
class OrdenTrabajoForm(forms.ModelForm):
    tipo_mantenimiento = forms.ChoiceField(choices=OrdenMantenimiento.sel_tmantenimiento, required=False)
    tipo_de_combustible = forms.ChoiceField(choices=OrdenCombustible.sel_tcombustible, required=False)
    cantidad_galones = forms.CharField(max_length=45, required=False)
    cantidad_galones_detalle = forms.CharField(max_length=45, required=False)
    tecnico = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput(), required=False)
    fecha = forms.DateField(initial=timezone.now().date(), widget=forms.HiddenInput())

    class Meta:
        model = OrdendeTrabajo
        fields = '__all__'
        
    def save(self, commit=True):
        orden_trabajo = super().save(commit=False)
        if commit:
            orden_trabajo.save()
            if self.cleaned_data['tipo_orden'] == 'Mantenimiento':
                OrdenMantenimiento.objects.create(ordende_trabajo=orden_trabajo, tipo_mantenimiento=self.cleaned_data['tipo_mantenimiento'])
            else:
                OrdenCombustible.objects.create(ordende_trabajo=orden_trabajo, tipo_de_combustible=self.cleaned_data['tipo_de_combustible'], cantidad_galones=self.cleaned_data['cantidad_galones'], cantidad_galones_detalle=self.cleaned_data['cantidad_galones_detalle'])
        return orden_trabajo
'''
#buzon de quejas form
class QuejaSugerenciaForm(forms.ModelForm):
    class Meta:
        model = QuejaSugerencia
        fields = ['circuito', 'subcircuito', 'tipo', 'detalles', 'contacto', 'nombres', 'apellidos']