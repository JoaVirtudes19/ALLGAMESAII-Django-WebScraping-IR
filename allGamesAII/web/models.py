from django.db import models

# Create your models here.


class Juego(models.Model):
    nombre = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    urlImg = models.CharField(max_length=200)
    descripcion = models.TextField()
    nota = models.FloatField()
    descuento = models.IntegerField()
    generos = models.TextField()
    plataforma = models.CharField(max_length=30)
    tienda = models.CharField(max_length=15)


    def __str__(self):
        return self.nombre