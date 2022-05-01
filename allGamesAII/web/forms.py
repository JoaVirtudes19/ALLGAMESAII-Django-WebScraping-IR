from dataclasses import fields
from inspect import classify_class_attrs
from django import forms
from django.forms import ModelForm
from web.models import Genero, Plataforma


#Archivo para crear formularios


class BusquedaTitulo(forms.Form):
    nombreJuego = forms.CharField(label="Nombre del juego", widget=forms.TextInput, required=True)

class BuscarGenero(forms.Form):
    genero = forms.ModelChoiceField(label="Seleccione un género", queryset=Genero.objects.all().order_by("nombre"))

class BuscarPlataforma(forms.Form):
    plataforma = forms.ModelChoiceField(label="Seleccione una plataforma", queryset=Plataforma.objects.all())