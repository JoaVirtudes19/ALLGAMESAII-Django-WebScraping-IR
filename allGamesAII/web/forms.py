from inspect import classify_class_attrs
from django import forms
from django.forms import ModelForm

from web.models import Juego

#Archivo para crear formularios


class BusquedaTitulo(forms.Form):
    nombreJuego = forms.CharField(label="Nombre del juego", widget=forms.TextInput, required=True)