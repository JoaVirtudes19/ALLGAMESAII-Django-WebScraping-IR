from django.http import HttpResponseRedirect
from django.shortcuts import render
from web.forms import BusquedaTitulo
from web.models import Juego
from web import cargaDatos
# Create your views here.

def prueba(request):
    juegos = Juego.objects.all().order_by('-fecha')
    return render(request,'inicio.html',{"juegos":juegos})


def juego(request,id_juego):
    juego = Juego.objects.get(id=id_juego)
    return render(request,'juego.html',{"juego":juego})

def cargar(request):
    if request.method == 'POST':
        if cargaDatos.almacenar("pruebaIndice"):
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
            ##Función para hacer una busqueda en whoosh
            print(nombre)
    else:
        form = BusquedaTitulo()
    return render(request,'buscarTitulo.html',{'form':form})