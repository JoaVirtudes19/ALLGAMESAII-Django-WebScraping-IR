from django.db import models
from django.contrib.auth.models import User

# Create your models here.

##Usar sistema de recomendación colab, añadir pantalla de inicio al usuario para seleccionar las categorais que le gustan
#Podemos añadir una clave primaria
#Crear los juegos sin los enlaces y guardar en un diccionario para 
#seguidamente añadirlo después de un bulk (django 3)

class Gusto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generoInteresado =  models.ForeignKey('Genero',on_delete=models.CASCADE)
    visitas = models.IntegerField()
class Tienda(models.Model):
    tienda = models.CharField(max_length=20)
    def __str__(self):
        return self.tienda
class Plataforma(models.Model):
    nombre = models.TextField(unique=True)
    def __str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.TextField(unique=True)
    def __str__(self):
        return self.nombre


class Juego(models.Model):
    nombre = models.TextField()
    url = models.TextField()
    urlImg =models.TextField()
    descripcion = models.TextField()
    nota = models.FloatField()
    precio = models.FloatField()
    descuento = models.IntegerField()
    fecha = models.DateField(null=True)
    genero = models.ManyToManyField(Genero)
    plataforma = models.ForeignKey(Plataforma,on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda,on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre