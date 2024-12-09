# Generated by Django 4.2.15 on 2024-12-05 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0016_delete_seleccion'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoJugadora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('estado', models.CharField(choices=[('JUEGA', 'Juega'), ('NO_JUEGA', 'No Juega'), ('LESION', 'Lesionada'), ('OTROS', 'Otros')], max_length=20)),
                ('posiciones', models.CharField(max_length=100)),
                ('observaciones', models.TextField(blank=True)),
                ('jugadora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jugadoras.jugadoraporano')),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]