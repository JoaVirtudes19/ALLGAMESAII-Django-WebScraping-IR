from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from web.forms import BuscarGenero, BusquedaDescripcion, BusquedaTitulo, BuscarPlataforma,BuscarTituloGenero,BuscarTituloTienda
from web.models import Juego,Genero,Gusto
from web import cargaDatos
from web.whoosh import descripcionWhoosh, tituloWhoosh, tituloGeneroWhoosh,tituloTiendaWhoosh
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from web.recomendaciones import *
# Create your views here.

nombreIndice = "pruebaIndice"

def inicio(request):
    juegos = Juego.objects.all().order_by('-fecha')
    return render(request,'inicio.html',{"juegos":juegos})

def recomendacion(request):
    juegos = list()
    if not request.user.is_anonymous:
        recomendaciones=recomendarJuegos(request.user)
        juegos = [ Juego.objects.get(id=id) for id,puntuacion in recomendaciones]
    return render(request,'recomendar.html',{"juegos":juegos})

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
            return render(request,"login.html",{'error':"Usuario o contraseña incorrectos"})
        else:
            return render(request,'login.html')
    else:
        return HttpResponseRedirect("/inicio")

#ARREGLAR ERROR AL NO PONER LA CABLE CORRECTA EN REGISTRO
def registrarse(request):
    if request.user.is_anonymous:
        #Registro
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/login")
            else:
                errores = form.errors.as_data()
                form = UserCreationForm()
                return render(request,"registro.html",{'errores':errores,'form':form})
        else:
            form = UserCreationForm()
            return render(request,'registro.html',{"form":form})
    else:
        return HttpResponseRedirect("/inicio")

def juego(request,id_juego):
    juego = Juego.objects.get(id=id_juego)
    generos = juego.genero.all()
    #Aumentamos el número de visitas para el genero relacionado con el usuario
    if not request.user.is_anonymous:
        for genero in generos:
            gusto,creado = Gusto.objects.get_or_create(generoInteresado=genero,user=request.user,defaults={'visitas':1})
            if not creado:
                gusto.visitas = gusto.visitas + 1
                gusto.save()
    return render(request,'juego.html',{"juego":juego,"generos":generos})

@login_required(login_url="/login/")
def cargar(request):
    #Borrar esto
    load_similarities()
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
    titulo = "Buscar por Título"
    url =  '/buscarTitulo/'
    if request.method == 'POST':
        form = BusquedaTitulo(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombreJuego']
            juegos = tituloWhoosh(nombreIndice,nombre)
            return render(request,"buscar.html",{'form':form,"juegos":juegos,'titulo':titulo,'url':url})
    else:
        form = BusquedaTitulo()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})

def buscarDescripcion(request):
    titulo = "Buscar por Descripción"
    url =  '/buscarDescripcion/'
    if request.method == 'POST':
        form = BusquedaDescripcion(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['descripcion']
            juegos = descripcionWhoosh(nombreIndice,nombre)
            return render(request,"buscar.html",{'form':form,"juegos":juegos,'titulo':titulo,'url':url})
    else:
        form = BusquedaDescripcion()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})

def buscarGenero(request):
    titulo = "Buscar por Genero"
    url =  '/buscarGenero/'
    if request.method == 'POST':
        form = BuscarGenero(request.POST)
        if form.is_valid():
            genero = form.cleaned_data['genero']
            #g=Genero.objects.get(genero)    
            juegos = genero.juego_set.all()
            #juegos = Juego.objects.all().filter(genero=genero).order_by("-nota")
            return render(request,'buscar.html',{'form':form,'juegos':juegos,'titulo':titulo,'url':url})
    else:
        form = BuscarGenero()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})

def buscarTituloGenero(request):
    titulo = "Buscar por Título y Género"
    url =  '/buscarTituloGenero/'
    if request.method == 'POST':
        form = BuscarTituloGenero(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombreJuego']
            genero = form.cleaned_data['genero']
            juegos = tituloGeneroWhoosh(nombreIndice,nombre,genero)
            return render(request,'buscar.html',{'form':form,'juegos':juegos,'titulo':titulo,'url':url})
    else:
        form = BuscarTituloGenero()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})

def buscarTituloTienda(request):
    titulo = "Buscar por Título y Tienda"
    url =  '/buscarTituloTienda/'
    if request.method == 'POST':
        form = BuscarTituloTienda(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombreJuego']
            tienda = form.cleaned_data['tienda']
            juegos = tituloTiendaWhoosh(nombreIndice,nombre,tienda)
            return render(request,'buscar.html',{'form':form,'juegos':juegos,'titulo':titulo,'url':url})
    else:
        form = BuscarTituloTienda()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})

def buscarPlataforma(request):
    titulo = "Buscar por Plataforma"
    url =  '/buscarPlataforma/'
    if request.method == 'POST':
        form = BuscarPlataforma(request.POST)
        if form.is_valid():
            plataforma = form.cleaned_data['plataforma']
            juegos = Juego.objects.all().filter(plataforma=plataforma).order_by("-nota")
            return render(request,'buscar.html',{'form':form,'juegos':juegos,'titulo':titulo,'url':url})
    else:
        form = BuscarPlataforma()
        return render(request,'buscar.html',{'form':form,'titulo':titulo,'url':url})