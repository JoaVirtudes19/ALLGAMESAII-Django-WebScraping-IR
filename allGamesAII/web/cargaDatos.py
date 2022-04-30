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
from web.models import Juego
from web.models import Tienda
from web.models import Genero
from web.models import Plataforma
#Para transformar las fechas
import locale
locale.setlocale(locale.LC_TIME, '')
def crearTiendas():
    Tienda.objects.create(nombre="Instant-Gaming")
    Tienda.objects.create(nombre="Kinguin")

def crearJuego(nombre,url,urlImg,descripcion,nota,descuento,stringGeneros,stringPlataforma,tienda,fecha):
    #Creamos la plataforma
    #AÑADIR DETECTAR PLATAFORMA PARA NO AÑADIR REPETIDAS
    plataforma, creado = Plataforma.objects.get_or_create(nombre=stringPlataforma)
    #Creamos el juego
    juego = Juego.objects.create(nombre=nombre,url=url,urlImg=urlImg,descripcion=descripcion,nota=nota
    ,descuento=descuento,plataforma=plataforma,tienda=tienda,fecha=fecha)
    #Añadimos los generos a el juego
    for stringGenero in stringGeneros.split(','):
        genero, creado = Genero.objects.get_or_create(nombre=stringGenero,tienda=tienda)
        juego.genero.add(genero)


def almacenar(nombreIndice):
    #Eliminamos todos los registros de la base de datos
    Juego.objects.all().delete()
    Plataforma.objects.all().delete()
    Genero.objects.all().delete()
    Tienda.objects.all().delete()
    crearTiendas()
    #Creamos el indice
    schema = Schema(nombre=TEXT(),url=ID(stored=True),descripcion=TEXT()) #Dejamos descripción y nombre como no stored, ya que este dato lo tenemos el django
    if not os.path.exists(nombreIndice):
        os.mkdir(nombreIndice)
    ix = create_in(nombreIndice,schema=schema)
    cargaInst = instGaming(nombreIndice)
    #cargaKing = kingGaming(wr)
    return cargaInst

##AÑADIR UN PARAMETRO DE ENTRADA PARA INDICAR CUANTAS PÁGINAS CARGAR COMO MÁXIMO
#La plataforma debe de coincidir en los scraping, así que mejor reconocerla y ponerla de de forma generica para nuestro comparador.
#Falta añadir fecha de salida del producto

def instGaming(nombreIndice):
    try:
        ix = open_dir(nombreIndice)
        wr = ix.writer()
        tienda = Tienda.objects.get(nombre="Instant-Gaming")
        for pag in range(1,2):
            req = urllib.request.Request("https://www.instant-gaming.com/es/busquedas/?page=" + str(pag), headers={'User-Agent': 'Mozilla/5.0'})
            f = urllib.request.urlopen(req)
            s = BeautifulSoup(f, "lxml")
            juegos = s.find("div",class_="listing-games").find_all("div","force-badge")
            for div in juegos:
                url = str(div.a['href'])
                nombre = str(list(div.find("div",class_="name").stripped_strings)[-1])
                descuentoDiv = div.find("div",class_="discount")
                #Podemos no tener descuento
                if descuentoDiv != None:
                    descuento = int(str(descuentoDiv.string).replace('-','').replace('%',''))
                else:
                    descuento = 0
                notaDiv = div.find("div","ig-search-reviews-avg")
                if notaDiv != None:
                    nota = float(str(notaDiv.string))/2
                else:
                    nota = 0.0
                #Carga de la imagen
                urlImg = str(div.find("img",class_="picture")['data-src'])
                #Buscamos dentro del juego
                req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                f2 = urllib.request.urlopen(req2)
                s2 = BeautifulSoup(f2, "lxml")
                divDes=s2.find("div",class_="readable")
                if divDes != None:
                    descripcion = "".join(list(divDes.stripped_strings))
                else:
                    descripcion = ""
                plataformaDiv = s2.find("div",class_="subinfos").a
                if plataformaDiv != None:
                    plataforma = str(list(plataformaDiv.stripped_strings)[0])
                else:
                    plataforma  = "Indefinida"
                generosDiv = s2.find("div",class_="table-cell",string="Género:").next_sibling.next_sibling
                if generosDiv != None:
                    aS = list(generosDiv.find_all("a"))
                    generos = aS[0].string
                    for a in aS[1:]:
                        generos = generos +','+a.string
                else:
                    generos = ""
                #FECHA
                fechaDiv = s2.find("div",class_="table-cell",string="Fecha de lanzamiento:").next_sibling.next_sibling
                if fechaDiv != None:
                    #Tenemos que añadir un filtro para las fechas de reserva EN, por ahroa añadimos None
                    if 'En' in str(fechaDiv.string):
                        fecha = None
                    else:
                        fecha = datetime.strptime(str(fechaDiv.string), ' %d %B %Y ').date()
                else:
                    fecha = None
                print(nombre)
                wr.add_document(nombre=nombre,url=url,descripcion=descripcion)
                crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generos,plataforma,tienda,fecha)
        wr.commit()
    except Exception as e:
        print(e)
        return False
    return True