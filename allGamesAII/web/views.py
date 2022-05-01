from django.http import HttpResponseRedirect
from django.shortcuts import render
from web.forms import BuscarGenero, BusquedaTitulo, BuscarPlataforma
from web.models import Juego
from web import cargaDatos
from web.whoosh import tituloWhoosh
# Create your views here.

nombreIndice = "pruebaIndice"

def prueba(request):
    juegos = Juego.objects.all().order_by('-fecha')
    return render(request,'inicio.html',{"juegos":juegos})


def juego(request,id_juego):
    juego = Juego.objects.get(id=id_juego)
    return render(request,'juego.html',{"juego":juego})

def cargar(request):
    if request.method == 'POST':
        if cargaDatos.almacenar(nombreIndice):
            juegos = Juego.objects.all()
            n = juegos.count()
            return render(request,"cargados.html",{"n":n,"juegos":juegos})
        else:
            return render(request,"errorCargar.html")
    else:
        return render(request,"cargar.html")

def buscarTitulo(request):
    if request.method == 'POST':
        form = BusquedaTitulo(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombreJuego']
            juegos = tituloWhoosh(nombreIndice,nombre)
            return render(request,"buscarTitulo.html",{'form':form,"juegos":juegos})
    else:
        form = BusquedaTitulo()
        return render(request,'buscarTitulo.html',{'form':form})

def buscarGenero(request):
    if request.method == 'POST':
        form = BuscarGenero(request.POST)
        if form.is_valid():
            genero = form.cleaned_data['genero']
            juegos = Juego.objects.all().filter(genero=genero).order_by("-nota")
            return render(request,'buscarGenero.html',{'form':form,'juegos':juegos})
    else:
        form = BuscarGenero()
        return render(request,'buscarGenero.html',{'form':form})

def buscarPlataforma(request):
    if request.method == 'POST':
        form = BuscarPlataforma(request.POST)
        if form.is_valid():
            plataforma = form.cleaned_data['plataforma']
            juegos = Juego.objects.all().filter(plataforma=plataforma).order_by("-nota")
            return render(request,'buscarPlataforma.html',{'form':form,'juegos':juegos})
    else:
        form = BuscarPlataforma()
        return render(request,'buscarPlataforma.html',{'form':form})