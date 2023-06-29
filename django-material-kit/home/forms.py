
from django import forms
from .models import PartePolicial

#crear parte policial
class PartePolicialForm(forms.ModelForm):
    class Meta:
        model = PartePolicial
        fields = ['tipo_parte', 'observaciones']