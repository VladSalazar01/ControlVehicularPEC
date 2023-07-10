
from django import forms
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from .models import *
from django.contrib.auth.models import Group

#crear parte policial
class PartePolicialForm(forms.ModelForm):
    class Meta:
        model = PartePolicial
        fields = ['tipo_parte', 'observaciones']

#crear usuario----
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
    subcircuito = forms.ModelChoiceField(queryset=Subcircuitos.objects.all(), required=False, label='Subcircuito')
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
            self.fields['subcircuito'].initial = personal_policial_instance.subcircuito

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        if 'identificacion' in exclude:
            exclude.remove('identificacion')  # No incluir 'identificacion' en la validación de unicidad

        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            self._update_errors(e)