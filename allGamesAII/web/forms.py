from dataclasses import fields
from inspect import classify_class_attrs
import re
from django import forms
from django.forms import ModelForm
from web.models import Genero, Plataforma,Tienda


#Archivo para crear formularios


class BusquedaTitulo(forms.Form):
    nombreJuego = forms.CharField(label="Nombre del juego", widget=forms.TextInput, required=True)

class BusquedaDescripcion(forms.Form):
    descripcion = forms.CharField(label="Palabras contenidas en la descripción", widget=forms.TextInput, required=True)

class BuscarGenero(forms.Form):
    genero = forms.ModelChoiceField(label="Seleccione un género", queryset=Genero.objects.all().order_by("nombre"))

class BuscarPlataforma(forms.Form):
    plataforma = forms.ModelChoiceField(label="Seleccione una plataforma", queryset=Plataforma.objects.all())

class BuscarTituloGenero(forms.Form):
    nombreJuego = forms.CharField(label="Nombre del juego", widget=forms.TextInput, required=True)
    genero = forms.ModelChoiceField(required=True,label="Seleccione un género", queryset=Genero.objects.all().order_by("nombre"))

class BuscarTituloTienda(forms.Form):
    nombreJuego = forms.CharField(label="Nombre del juego", widget=forms.TextInput, required=True)
    tienda = forms.ModelChoiceField(required=True,label="Seleccione una tienda", queryset=Tienda.objects.all())