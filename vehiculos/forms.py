
from django import forms
from .models import Solicitud, Checklist

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['vehiculo']

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['kilometraje', 'extintor', 'observaciones']