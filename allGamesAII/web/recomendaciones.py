from web.models import Juego,Gusto
from collections import Counter
import shelve

def load_similarities():
    shelf = shelve.open('dataRS.dat')
    shelf['juegos'] = obtenerVectoresJuegos()
    shelf.close()



## Hacer cambios en esta función
def recomendarJuegos(user):
    shelf = shelve.open("dataRS.dat")
    juegos = shelf['juegos']
    vector_usuario = list()
    porcentajes = dict()
    for gusto in user.gusto_set.all().order_by('visitas'):
        vector_usuario.append(gusto.generoInteresado.id)
    if len(vector_usuario) == 0:
        return []
    if len(vector_usuario) > 10:
        vector_usuario=set(vector_usuario[10:])
    else:
        vector_usuario=set(vector_usuario)
    for id_juego in juegos:
        x=dice_coefficient(vector_usuario,juegos[id_juego])
        porcentajes[id_juego]=x
    recomendados = sorted(porcentajes.items(), key=lambda x: x[1], reverse=True)[:100]
    print(recomendados)
    return recomendados

def obtenerVectoresJuegos():
    juegos = {}
    for juego in Juego.objects.all():
        id_juego  = juego.id
        juegos.setdefault(id_juego, set())
        generos = juego.genero.all()
        for genero in generos:
            juegos[id_juego].add(genero.id)
    return juegos

def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))