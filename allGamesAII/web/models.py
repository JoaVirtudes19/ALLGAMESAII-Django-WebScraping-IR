from django.db import models

# Create your models here.


class Tienda(models.Model):
    nombre = models.CharField(max_length=20)
    def __str__(self):
        return self.nombre

class Plataforma(models.Model):
    nombre = models.CharField(max_length=20)
    def __str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.CharField(max_length=20)
    tienda = models.ForeignKey(Tienda,on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre


class Juego(models.Model):
    #FALTA AÑADIR LA FECHA Y AL CREARLA datetime.date() NO NECESITAMOS LA HORA
    nombre = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    urlImg = models.CharField(max_length=200)
    descripcion = models.TextField()
    nota = models.FloatField()
    descuento = models.IntegerField()
    fecha = models.DateField(null=True)
    genero = models.ManyToManyField(Genero)
    plataforma = models.ForeignKey(Plataforma,on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda,on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre