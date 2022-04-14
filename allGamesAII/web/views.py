from django.shortcuts import render
from web import cargaDatos
# Create your views here.

def prueba(request):
    return render(request,'prueba.html')


def cargar(request):
    #Hacemos el scraping y lo guardamos en whoosh
    cargaDatos.almacenar("pruebaIndice")
    return render(request,'cargar.html')