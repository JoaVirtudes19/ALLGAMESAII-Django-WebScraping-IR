from mailbox import NoSuchMailboxError
import os
from re import T
import string
import urllib.request
from bs4 import BeautifulSoup
import lxml
from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh import qparser,query
from datetime import datetime
from web.models import Juego, Tienda
from web.models import Genero
from web.models import Plataforma
#Para transformar las fechas
import locale
locale.setlocale(locale.LC_TIME, '')

traduccion = {"fps":"fps / tps","aventura":"aventuras","cooperación":"cooperativo","indies":"indie","plataforma":"plataformas"
,"cooperativa local":"cooperativo local"}
def almacenar(nombreIndice):
    #Eliminamos todos los registros de la base de datos
    Juego.objects.all().delete()
    Plataforma.objects.all().delete()
    Genero.objects.all().delete()
    Tienda.objects.all().delete()
    schema = Schema(nombre=TEXT(),url=ID(stored=True),descripcion=TEXT()) #Dejamos descripción y nombre como no stored, ya que este dato lo tenemos el django
    if not os.path.exists(nombreIndice):
        os.mkdir(nombreIndice)
    ix = create_in(nombreIndice,schema=schema)
    pags=10
    cargaEneba = scraping_Eneba(nombreIndice,pags)
    cargaInst = scraping_InstantGaming(nombreIndice,pags)
    resultado = cargaInst and cargaEneba
    print(resultado)
    return resultado

def crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generos,plataforma,fecha,precio,tienda,dicGeneros,listaJuegos):
    juego = Juego(nombre=nombre,url=url,urlImg=urlImg,descripcion=descripcion,nota=nota
    ,descuento=descuento,plataforma=plataforma,fecha=fecha,precio=precio,tienda=tienda)
    listaJuegos.append(juego)
    dicGeneros[url] = generos
    return dicGeneros,listaJuegos

def crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda):
    generosTotales = [ Genero(nombre=nombre) for nombre in generosTotales]
    Genero.objects.bulk_create(generosTotales,ignore_conflicts=True)
    print("GENEROS CREADOS")
    Juego.objects.bulk_create(listaJuegos)
    print("JUEGOS CREADOS")
    for juego in Juego.objects.all().filter(tienda=tienda):
        for genr in dicGeneros[juego.url]:
            juego.genero.add(Genero.objects.get(nombre=genr))


#################################### SCRAPING INSTANTGAMING ####################################

def scraping_InstantGaming(nombreIndice,pags):
    generosTotales = list()
    plataformas = dict()
    dicGeneros = dict()
    listaJuegos = list()
    try:
        tienda, creada = Tienda.objects.get_or_create(tienda = "InstantGaming")
        print("Empezamos INSTANTGAMING")
        #Abrimos el índice
        ix = open_dir(nombreIndice)
        wr = ix.writer()
        for pag in range(1,pags+1):
            try: #Miramos en la pag
                req = urllib.request.Request("https://www.instant-gaming.com/es/busquedas/?page=" + str(pag), headers={'User-Agent': 'Mozilla/5.0'})
                f = urllib.request.urlopen(req,timeout=3)
                s = BeautifulSoup(f, "lxml")
                juegos = s.find("div",class_="listing-games").find_all("div","force-badge")
                for div in juegos:
                    url = url_InstantGaming(div)
                    print(url)
                    nombre = nombre_InstantGaming(div)
                    precio = precio_InstantGaming(div)
                    descuento = descuento_InstantGaming(div)
                    nota = nota_InstantGaming(div)
                    urlImg = urlImg_InstantGaming(div)
                    try: #Creamos el juego
                        req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        f2 = urllib.request.urlopen(req2,timeout=3)
                        s2 = BeautifulSoup(f2, "lxml")
                        descripcion = descripcion_InstantGaming(s2)
                        fecha = fecha_InstantGaming(s2)
                        plataforma,plataformas = plataforma_InstantGaming(s2,plataformas)
                        generosJuego,generosTotales = generos_InstantGaming(s2,generosTotales)
                        wr.add_document(nombre=nombre,url=url,descripcion=descripcion) #Lo añadimos al índice
                        dicGeneros,listaJuegos = crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generosJuego,plataforma,fecha,precio,tienda,dicGeneros,listaJuegos)
                    except Exception as e: #Timeout o error en la carga del juego
                        print(e)
            except Exception as e: #Timeout o error en la carga de la pag
                print(e)
        crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda)
        wr.commit()
    except Exception as e: #Error General
        print(e)
        return False
    return True

def nombre_InstantGaming(soup):
    return str(list(soup.find("div",class_="name").stripped_strings)[-1])

def url_InstantGaming(soup):
    return str(soup.a['href'])

def urlImg_InstantGaming(soup):
    return str(soup.find("img",class_="picture")['data-src'])

def descripcion_InstantGaming(soup):
    divDes=soup.find("div",class_="readable")
    if divDes != None:
        descripcion = "".join(list(divDes.stripped_strings))
    else:
        descripcion = ""
    return descripcion

def nota_InstantGaming(soup):
    notaDiv = soup.find("div","ig-search-reviews-avg")
    if notaDiv != None:
        nota = float(str(notaDiv.string))/2 #Dividimos entre 2 para tenerlo sobre 5, iguale que Eneba
    else:
        nota = 0.0
    return nota

def descuento_InstantGaming(soup):
    descuentoDiv = soup.find("div",class_="discount")
    #Podemos no tener descuento
    if descuentoDiv != None:
        descuento = int(str(descuentoDiv.string).replace('-','').replace('%',''))
    else:
        descuento = 0
    return descuento

def generos_InstantGaming(soup,generosTotales):
    generosDiv = soup.find("div",class_="table-cell",string="Género:")
    if generosDiv != None:
        generosDiv = generosDiv.next_sibling.next_sibling
        generos = list(generosDiv.find_all("a"))
    else:
        generos = []
    generosJuego = []
    for a in generos:
        genero = str(a.string).lower()
        if genero in traduccion:
            genero = traduccion[genero]
        generosJuego.append(genero)
        generosTotales.append(genero)
    return generosJuego,generosTotales

def plataforma_InstantGaming(soup,plataformas):
    plataformaDiv = soup.find("div",class_="subinfos").a
    if plataformaDiv != None:
        plataformaS = str(list(plataformaDiv.stripped_strings)[0]).lower()
    else:
        plataformaS = "Indefinida"
    if plataformaS not in plataformas:
        plat,creada = Plataforma.objects.get_or_create(nombre=plataformaS)
        plataformas[plataformaS] = plat
    plataforma = plataformas[plataformaS]
    return plataforma,plataformas

def fecha_InstantGaming(soup):
    fechaDiv = soup.find("div",class_="table-cell",string="Fecha de lanzamiento:")
    if fechaDiv != None:
        fechaDiv = fechaDiv.next_sibling.next_sibling
        if 'En' in str(fechaDiv.string):
            fecha = None
        else:
            fecha = datetime.strptime(str(fechaDiv.string), ' %d %B %Y ').date()
    else:
        fecha = None
    return fecha

def precio_InstantGaming(soup):
    precioDiv = soup.find("div",class_="price")
    #Podemos no tener descuento
    if precioDiv != None:
        precio = float(str(precioDiv.string).replace('€',''))
    else:
        precio = 0.0
    return precio

#################################### SCRAPING ENEBA ####################################

def scraping_Eneba(nombreIndice,pags):
    generosTotales = list()
    plataformas = dict()
    dicGeneros = dict()
    listaJuegos = list()
    try:
        tienda ,creada = Tienda.objects.get_or_create(tienda="Eneba")
        print("Empezamos ENEBA")
        ix = open_dir(nombreIndice)
        wr = ix.writer()
        for pag in range(1,pags*2+1):
            try:
                req = urllib.request.Request("https://www.eneba.com/es/store/games?page=" + str(pag) +"&platforms[]=BETHESDA&platforms[]=BLIZZARD&platforms[]=EPIC_GAMES&platforms[]=GOG&platforms[]=ORIGIN&platforms[]=OTHER&platforms[]=STEAM&platforms[]=UPLAY&regions[]=global&sortBy=POPULARITY_DESC&types[]=game", headers={'User-Agent': 'Mozilla/5.0'})
                f = urllib.request.urlopen(req,timeout=3)
                s = BeautifulSoup(f, "lxml")
                juegos = s.find("div",class_="JZCH_t").find_all("div",class_="pFaGHa")
                for div in juegos:
                    nombre = nombre_Eneba(div)
                    url = url_Eneba(div)
                    urlImg = urlImg_Eneba(div)
                    descuento = descuento_Eneba(div)
                    precio = precio_Eneba(div)
                    try: #Entramos en el juego
                        req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        f2 = urllib.request.urlopen(req2,timeout=3)
                        s2 = BeautifulSoup(f2, "lxml")
                        nota = nota_Eneba(s2)
                        plataforma,plataformas = plataforma_Eneba(s2,plataformas)
                        descripcion = descripcion_Eneba(s2)
                        fecha = fecha_Eneba(s2)
                        generosJuego,generosTotales = generos_Eneba(s2,generosTotales)
                        print(url)
                        wr.add_document(nombre=nombre,url=url,descripcion=descripcion)
                        dicGeneros,listaJuegos = crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generosJuego,plataforma,fecha,precio,tienda,dicGeneros,listaJuegos)
                    except Exception as e: #Timeout o error en la carga del juego
                        print(e)
            except Exception as e: #Timeout o error en la carga de la página
                   print(e) 
        crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda)
        wr.commit()
    except Exception as e: #Error general
        print(e)
        return False
    return True


def nombre_Eneba(soup):
    return str(soup.span.string)

def url_Eneba(soup):
    return "https://www.eneba.com"+str(soup.a['href'])

def urlImg_Eneba(soup):
    return str(soup.img['src'])

def descuento_Eneba(soup):
    descuentoDiv = soup.find("div",class_="PIG8fA")
    #Podemos no tener descuento
    if descuentoDiv != None:
        descuento = int(str(descuentoDiv.string).split(' ')[1].replace('%',''))
    else:
        descuento = 0
    return descuento

def precio_Eneba(soup):
    precioSpan = soup.find("span",class_="DTv7Ag").find("span",class_="L5ErLT")
    #Podemos no tener descuento
    if precioSpan != None:
        precioS = str(precioSpan.string).split(",")
        precio = float(precioS[0]+'.'+precioS[1][:2])
    else:
        precio = 0.0
    return precio

def nota_Eneba(soup):
    strongPuntuacion = soup.find("strong",class_="d52_Iq")
    if strongPuntuacion != None:
        nota = float(str(strongPuntuacion.string))
    else:
        nota = 0.0
    return nota

def plataforma_Eneba(soup,plataformas):
    strongPlataforma = list(soup.find_all("strong",class_="cEhl9f"))[1]
    if strongPlataforma != None:
        plataformaS = str(strongPlataforma.string).lower()
    else:
        plataformaS = "Indefinida"
    if plataformaS not in plataformas:
        plat,creada = Plataforma.objects.get_or_create(nombre=plataformaS)
        plataformas[plataformaS] = plat
    plataforma = plataformas[plataformaS]
    return plataforma,plataformas

def descripcion_Eneba(soup):
    descripcionDiv = soup.find("div",{'class':['Wz6WhX', 'XxYK78', 'L6cSBv']})
    #Podemos no tener descuento
    if descripcionDiv != None:
        descripcion = "".join(list(descripcionDiv.stripped_strings))
    else:
        descripcion = ""
    return descripcion

def fecha_Eneba(soup):
    fechaDiv = soup.find("div",class_="URplpg",string="Fecha de lanzamiento").next_sibling
    if fechaDiv != None:
        if 'En' in str(fechaDiv.string):
            fecha = None
        else:
            fecha = datetime.strptime(str(fechaDiv.string), '%d de %B de %Y').date()
    else:
        fecha = None
    return fecha

def generos_Eneba(soup,generosTotales):
    generosUl = soup.find("ul",class_="aoHRvN")
    generosJuego = []
    if generosUl != None:
        for li in generosUl:
            genero = str(list(li.stripped_strings)[0]).lower()
            if genero in traduccion:
                genero = traduccion[genero]
            generosJuego.append(genero)
            generosTotales.append(genero)
    return generosJuego,generosTotales