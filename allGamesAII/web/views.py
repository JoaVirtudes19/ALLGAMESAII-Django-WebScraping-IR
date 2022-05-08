from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from web.forms import BuscarGenero, BusquedaDescripcion, BusquedaTitulo, BuscarPlataforma
from web.models import Juego
from web import cargaDatos
from web.whoosh import descripcionWhoosh, tituloWhoosh
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.

nombreIndice = "pruebaIndice"

def inicio(request):
    juegos = Juego.objects.all().order_by('-fecha')
    return render(request,'inicio.html',{"juegos":juegos})

@login_required(login_url="/login/")
def cerrarSesion(request):
    logout(request)
    return HttpResponseRedirect("/inicio")

def iniciarSesion(request):
    if request.user.is_anonymous:
        #Iniciamos sesión
        if request.method == 'POST':
            usuario=request.POST["username"]
            contraseña=request.POST["password"]
            access = authenticate(username=usuario,password=contraseña)
            if access != None:
                if access.is_active:
                    login(request,access)
                    return HttpResponseRedirect("/inicio")
            #Mensaje error login
            return render(request,"errorCargar.html")

        else:
            form = AuthenticationForm()
            return render(request,'login.html',{"form":form})
    else:
        return HttpResponseRedirect("/inicio")

def registrarse(request):
    if request.user.is_anonymous:
        #Registro
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/login")
        else:
            form = UserCreationForm()
            return render(request,'registro.html',{"form":form})
    else:
        return HttpResponseRedirect("/inicio")

def juego(request,id_juego):
    juego = Juego.objects.get(id=id_juego)
    generos = juego.genero.all()
    return render(request,'juego.html',{"juego":juego,"generos":generos})

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

def buscarDescripcion(request):
    if request.method == 'POST':
        form = BusquedaDescripcion(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['descripcion']
            juegos = descripcionWhoosh(nombreIndice,nombre)
            return render(request,"buscarDescripcion.html",{'form':form,"juegos":juegos})
    else:
        form = BusquedaDescripcion()
        return render(request,'buscarDescripcion.html',{'form':form})

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