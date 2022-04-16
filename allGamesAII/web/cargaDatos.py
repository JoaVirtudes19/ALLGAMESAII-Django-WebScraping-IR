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
import requests
from web.models import Juego


def almacenar(nombreIndice):
    Juego.objects.all().delete()
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
                #response = requests.get(urlImg).content
                imagename = "imagenesPrueba" + '/' + nombre + '.jpg'
                #if not os.path.exists(imagename):
                #    with open(imagename, 'wb') as file:
                #        file.write(response)


                req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                f2 = urllib.request.urlopen(req2)
                s2 = BeautifulSoup(f2, "lxml")
                divDes=s2.find("div",class_="readable")
                if divDes != None:
                    descripcion = "".join(list(divDes.stripped_strings))
                else:
                    descripcion = ""
                print(nombre)
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

                wr.add_document(nombre=nombre,url=url,descripcion=descripcion)
                Juego.objects.create(nombre = nombre, url = url, urlImg = urlImg,descripcion = descripcion, nota = nota, descuento = descuento, generos = generos, plataforma = plataforma, tienda = "Instant Gaming")
        wr.commit()
    except:
        return False
    return True