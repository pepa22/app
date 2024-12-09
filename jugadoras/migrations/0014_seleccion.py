# Generated by Django 4.2.15 on 2024-09-09 16:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0013_alter_jugadora_dni'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seleccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.PositiveIntegerField()),
                ('jugadora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jugadoras.jugadora')),
            ],
        ),
    ]
