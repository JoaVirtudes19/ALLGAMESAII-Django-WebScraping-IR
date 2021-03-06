# Generated by Django 4.0.2 on 2022-04-30 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plataforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tienda', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Juego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('url', models.TextField()),
                ('urlImg', models.TextField()),
                ('descripcion', models.TextField()),
                ('nota', models.FloatField()),
                ('precio', models.FloatField()),
                ('descuento', models.IntegerField()),
                ('fecha', models.DateField(null=True)),
                ('genero', models.ManyToManyField(to='web.Genero')),
                ('plataforma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.plataforma')),
                ('tienda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.tienda')),
            ],
        ),
    ]
