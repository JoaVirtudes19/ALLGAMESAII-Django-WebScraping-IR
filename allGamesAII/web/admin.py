from django.contrib import admin
from web.models import Juego,Plataforma,Genero,Tienda,Gusto
# Register your models here.

admin.site.register(Tienda)
admin.site.register(Juego)
admin.site.register(Plataforma)
admin.site.register(Genero)
admin.site.register(Gusto)