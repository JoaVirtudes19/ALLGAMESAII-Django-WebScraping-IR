from django.db import models

# Create your models here.

##Usar sistema de recomendación colab, añadir pantalla de inicio al usuario para seleccionar las categorais que le gustan
#Podemos añadir una clave primaria
#Crear los juegos sin los enlaces y guardar en un diccionario para 
#seguidamente añadirlo después de un bulk (django 3)



class Plataforma(models.Model):
    nombre = models.TextField(primary_key=True)
    def __str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.TextField(primary_key=True)
    def __str__(self):
        return self.nombre


class Juego(models.Model):
    nombre = models.CharField(max_length=30)
    url = models.CharField(max_length=200,primary_key=True )
    urlImg = models.CharField(max_length=200)
    descripcion = models.TextField()
    nota = models.FloatField()
    descuento = models.IntegerField()
    fecha = models.DateField(null=True)
    genero = models.ManyToManyField(Genero)
    plataforma = models.ForeignKey(Plataforma,on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre