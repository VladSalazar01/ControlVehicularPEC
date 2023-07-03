
from django import forms
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

#crear parte policial
class PartePolicialForm(forms.ModelForm):
    class Meta:
        model = PartePolicial
        fields = ['tipo_parte', 'observaciones']

#crear usuario
class CombinedForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombres')
    last_name = forms.CharField(max_length=30, required=True, label='Apellidos')
    username = forms.CharField(max_length=30, required=True, label='Nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Contraseña')
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirmar contraseña')
    direccion = forms.CharField(widget=forms.Textarea(attrs={'maxlength': 200}), required=False, label='Dirección')
    fecha_de_nacimiento = forms.DateField(
        widget=forms.SelectDateWidget(years=range(date.today().year - 100, date.today().year - 18)),
        required=False,
        label='Fecha de nacimiento'
    )
    titular = forms.BooleanField(required=False, label='Titular')
    tipo_sange = forms.ChoiceField(
        choices=Usuario.tds, 
        required=False, 
        label='Tipo de sangre',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subcircuito = forms.ModelChoiceField(queryset=Subcircuitos.objects.all(), required=False, label='Subcircuito')
    role = forms.ChoiceField(choices=[('personal_policial', 'Personal Policial'), ('tecnico', 'Tecnico')], label='Rol')

    class Meta:
        model = Usuario
        fields = ['direccion', 'fecha_de_nacimiento', 'genero', 'identificacion', 'rango', 'tipo_sange']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data