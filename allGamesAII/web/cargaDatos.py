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


def crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda):
    generosTotales = [ Genero(nombre=nombre) for nombre in generosTotales]
    Genero.objects.bulk_create(generosTotales,ignore_conflicts=True)
    print("GENEROS CREADOS")
    Juego.objects.bulk_create(listaJuegos)
    print("JUEGOS CREADOS")
    for juego in Juego.objects.all().filter(tienda=tienda):
        for genr in dicGeneros[juego.url]:
            juego.genero.add(Genero.objects.get(nombre=genr))
def almacenar(nombreIndice):
    #Eliminamos todos los registros de la base de datos
    Juego.objects.all().delete()
    Plataforma.objects.all().delete()
    Genero.objects.all().delete()
    Tienda.objects.all().delete()
    #Creamos el indice
    schema = Schema(nombre=TEXT(),url=ID(stored=True),descripcion=TEXT()) #Dejamos descripción y nombre como no stored, ya que este dato lo tenemos el django
    if not os.path.exists(nombreIndice):
        os.mkdir(nombreIndice)
    ix = create_in(nombreIndice,schema=schema)
    pags=10
    cargaEneba = enebaGaming(nombreIndice,pags)
    cargaInst = instGaming(nombreIndice,pags)
    resultado = cargaInst and cargaEneba
    print(resultado)
    return resultado

##AÑADIR UN PARAMETRO DE ENTRADA PARA INDICAR CUANTAS PÁGINAS CARGAR COMO MÁXIMO
#La plataforma debe de coincidir en los scraping, así que mejor reconocerla y ponerla de de forma generica para nuestro comparador.
#Falta añadir fecha de salida del producto

def instGaming(nombreIndice,pags):
    def crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generos,plataforma,fecha,precio,tienda):
        #Creamos la plataforma
        juego = Juego(nombre=nombre,url=url,urlImg=urlImg,descripcion=descripcion,nota=nota
        ,descuento=descuento,plataforma=plataforma,fecha=fecha,precio=precio,tienda=tienda)
        listaJuegos.append(juego)
        dicGeneros[url] = generos
    #Creamos conjuntos para almacenar los generos y plataformas para seguidamente crearlos todos a la vez
    generosTotales = list()
    #Diccionario que almacena el juego con sus generos para relacionarlos más adelante
    plataformas = dict()
    dicGeneros = dict()
    listaJuegos = list()
    try:
        tienda, creada = Tienda.objects.get_or_create(tienda = "InstantGaming")
        print("Empezamos INSTANTGAMING")
        ix = open_dir(nombreIndice)
        wr = ix.writer()
        for pag in range(1,pags+1):
            try: #Intentamos mirar la pagina
                req = urllib.request.Request("https://www.instant-gaming.com/es/busquedas/?page=" + str(pag), headers={'User-Agent': 'Mozilla/5.0'})
                f = urllib.request.urlopen(req,timeout=3)
                s = BeautifulSoup(f, "lxml")
                juegos = s.find("div",class_="listing-games").find_all("div","force-badge")
                for div in juegos:
                    url = str(div.a['href'])
                    nombre = str(list(div.find("div",class_="name").stripped_strings)[-1])
                    precioDiv = div.find("div",class_="price")
                    #Podemos no tener descuento
                    if precioDiv != None:
                        precio = float(str(precioDiv.string).replace('€',''))
                    else:
                        precio = 0.0
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
                    try: #Creamos el juego
                        req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        f2 = urllib.request.urlopen(req2,timeout=3)
                        s2 = BeautifulSoup(f2, "lxml")
                        divDes=s2.find("div",class_="readable")
                        if divDes != None:
                            descripcion = "".join(list(divDes.stripped_strings))
                        else:
                            descripcion = ""

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
                        plataformaDiv = s2.find("div",class_="subinfos").a
                        if plataformaDiv != None:
                            plataformaS = str(list(plataformaDiv.stripped_strings)[0]).lower()
                        else:
                            plataformaS = "Indefinida"
                        if plataformaS not in plataformas:
                            plat,creada = Plataforma.objects.get_or_create(nombre=plataformaS)
                            plataformas[plataformaS] = plat
                        plataforma = plataformas[plataformaS]
                        generosDiv = s2.find("div",class_="table-cell",string="Género:").next_sibling.next_sibling
                        if generosDiv != None:
                            generos = list(generosDiv.find_all("a"))
                        else:
                            generos = []
                        generosJuego = []
                        for a in generos:
                            genero = str(a.string).lower()
                            generosJuego.append(genero)
                            generosTotales.append(genero)
                        #Añadir guardar comentarios en el scraping, todos pegados
                        print(url)
                        wr.add_document(nombre=nombre,url=url,descripcion=descripcion)
                        crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generosJuego,plataforma,fecha,precio,tienda)
                    except Exception as e:
                        print("Timeout")
                        print(e)
            except Exception as e:
                print("Timeout")
                print(e)
        crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda)
        wr.commit()
    except Exception as e:
        print(e)
        return False
    return True


def enebaGaming(nombreIndice,pags):
    def crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generos,plataforma,fecha,precio,tienda):
        #Creamos la plataforma
        juego = Juego(nombre=nombre,url=url,urlImg=urlImg,descripcion=descripcion,nota=nota
        ,descuento=descuento,plataforma=plataforma,fecha=fecha,precio=precio,tienda=tienda)
        listaJuegos.append(juego)
        dicGeneros[url] = generos
    #Creamos conjuntos para almacenar los generos y plataformas para seguidamente crearlos todos a la vez
    generosTotales = list()
    #Diccionario que almacena el juego con sus generos para relacionarlos más adelante
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
                    nombre = str(div.span.string)
                    url = "https://www.eneba.com"+str(div.a['href'])
                    urlImg = str(div.img['src'])
                    descuentoDiv = div.find("div",class_="PIG8fA")
                    #Podemos no tener descuento
                    if descuentoDiv != None:
                        descuento = int(str(descuentoDiv.string).split(' ')[1].replace('%',''))
                    else:
                        descuento = 0
                    #ENTRAMOS DENTRO DEL JUEGO
                    try:
                        req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        f2 = urllib.request.urlopen(req2,timeout=3)
                        s2 = BeautifulSoup(f2, "lxml")
                        precioSpan = div.find("span",class_="DTv7Ag").find("span",class_="L5ErLT")
                        #Podemos no tener descuento
                        if precioSpan != None:
                            precioS = str(precioSpan.string).split(",")
                            precio = float(precioS[0]+'.'+precioS[1][:2])
                        else:
                            precio = 0.0
                        strongPuntuacion = s2.find("strong",class_="d52_Iq")
                        if strongPuntuacion != None:
                            nota = float(str(strongPuntuacion.string))
                        else:
                            nota = 0.0
                        strongPlataforma = list(s2.find_all("strong",class_="cEhl9f"))[1]
                        if strongPlataforma != None:
                            plataformaS = str(strongPlataforma.string).lower()
                        else:
                            plataformaS = "Indefinida"
                        if plataformaS not in plataformas:
                            plat,creada = Plataforma.objects.get_or_create(nombre=plataformaS)
                            plataformas[plataformaS] = plat
                        plataforma = plataformas[plataformaS]
                        descripcionDiv = s2.find("div",{'class':['Wz6WhX', 'XxYK78', 'L6cSBv']})
                        #Podemos no tener descuento
                        if descripcionDiv != None:
                            descripcion = "".join(list(descripcionDiv.stripped_strings))
                        else:
                            descripcion = ""
                        fechaDiv = s2.find("div",class_="URplpg",string="Fecha de lanzamiento").next_sibling
                        if fechaDiv != None:
                            #Tenemos que añadir un filtro para las fechas de reserva EN, por ahroa añadimos None
                            if 'En' in str(fechaDiv.string):
                                fecha = None
                            else:
                                fecha = datetime.strptime(str(fechaDiv.string), '%d de %B de %Y').date()
                        else:
                            fecha = None
                        generosUl = s2.find("ul",class_="aoHRvN")
                        generosJuego = []
                        if generosUl != None:
                            for li in generosUl:
                                genero = str(list(li.stripped_strings)[0]).lower()
                                generosJuego.append(genero)
                                generosTotales.append(genero)
                        print(url)
                        wr.add_document(nombre=nombre,url=url,descripcion=descripcion)
                        crearJuego(nombre,url,urlImg,descripcion,nota,descuento,generosJuego,plataforma,fecha,precio,tienda)
                    except Exception as e:
                        print("Timeout")
                        print(e)
            except Exception as e:
                   print("Timeout")
                   print(e) 
        crearJuegos(dicGeneros,generosTotales,listaJuegos,tienda)
        wr.commit()
    except Exception as e:
        print(e)
        return False
    return True