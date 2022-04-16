from django.shortcuts import render
from web.models import Juego
from web import cargaDatos
# Create your views here.

def prueba(request):
    return render(request,'prueba.html')


def cargar(request):
    
    if cargaDatos.almacenar("pruebaIndice"):
        juegos = Juego.objects.all()
        n = juegos.count()
        return render(request,"cargar.html",{"n":n,"juegos":juegos})
    else:
        return render(request,"errorCargar.html")