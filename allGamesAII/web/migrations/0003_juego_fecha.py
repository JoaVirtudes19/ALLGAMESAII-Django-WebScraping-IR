# Generated by Django 4.0.2 on 2022-04-21 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_plataforma_tienda_remove_juego_generos_genero_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='juego',
            name='fecha',
            field=models.DateTimeField(null=True),
        ),
    ]