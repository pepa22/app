# Generated by Django 4.2.15 on 2024-12-06 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0022_posicion_remove_estadojugadora_posiciones_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TiposEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=3, unique=True)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='estadojugadora',
            name='estado',
        ),
        migrations.AddField(
            model_name='estadojugadora',
            name='estadoN',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jugadoras.tiposestado'),
        ),
    ]