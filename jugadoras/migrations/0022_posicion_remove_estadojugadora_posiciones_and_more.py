# Generated by Django 4.2.15 on 2024-12-05 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0021_alter_estadojugadora_posiciones'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=3, unique=True)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='estadojugadora',
            name='posiciones',
        ),
        migrations.AddField(
            model_name='estadojugadora',
            name='posiciones',
            field=models.ManyToManyField(blank=True, to='jugadoras.posicion'),
        ),
    ]
