import os
from re import T
import urllib.request
from bs4 import BeautifulSoup
import lxml
from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh import qparser,query
from datetime import datetime
import requests


def almacenar(nombreIndice):
    #Creamos el indice
    schema = Schema(tienda=ID(stored=True),titulo=TEXT(stored=True),url=ID(stored=True),img=ID(stored=True),urlImg=ID(stored=True),descripcion=TEXT(stored=True),nota=NUMERIC(float,stored=True),descuento=NUMERIC(stored=True))
    if not os.path.exists(nombreIndice):
        os.mkdir(nombreIndice)
    ix = create_in(nombreIndice,schema=schema)
    cargaInst = instGaming(nombreIndice)
    #cargaKing = kingGaming(wr)



def instGaming(nombreIndice):
    ix = open_dir(nombreIndice)
    wr = ix.writer()
    for pag in range(1,2):
        req = urllib.request.Request("https://www.instant-gaming.com/es/busquedas/?type%5B0%5D=steam&page=" + str(pag), headers={'User-Agent': 'Mozilla/5.0'})
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
            wr.add_document(tienda="INSTANTGAMING",titulo=nombre,url=url,img=imagename,urlImg=urlImg,descripcion=descripcion,nota=nota,descuento=descuento)
    wr.commit()
    return True


def kingGaming(nombreIndice):
    ix = open_dir(nombreIndice)
    wr = ix.writer()
    for pag in range(1,2):
        req = urllib.request.Request("https://www.instant-gaming.com/es/busquedas/?type%5B0%5D=steam&page=" + str(pag), headers={'User-Agent': 'Mozilla/5.0'})
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, "lxml")


if __name__ == '__main__':
    almacenar("pruebaIndice")