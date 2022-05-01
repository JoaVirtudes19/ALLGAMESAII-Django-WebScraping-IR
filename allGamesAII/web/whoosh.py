from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh import qparser,query
from web.models import Juego
def tituloWhoosh(nombreIndice,entrada):
    ix=open_dir(nombreIndice)
    with ix.searcher() as searcher:
        qp = qparser.QueryParser("nombre",ix.schema)
        q = qp.parse(entrada)#Aquí estamos buscando por frase al añadirle las comas.
        resultados = searcher.search(q,limit=None)
        juegos = [ Juego.objects.get(url=x['url']) for x in resultados]
    return juegos