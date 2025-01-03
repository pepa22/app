# Generated by Django 4.2.15 on 2024-08-30 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Jugadora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('dni', models.CharField(max_length=20, unique=True)),
                ('fecha_nacimiento', models.DateField()),
                ('num_socia', models.CharField(max_length=50, unique=True)),
                ('activa', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='JugadoraPorAno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jugadoras.categoria')),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jugadoras.division')),
                ('jugadora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jugadoras.jugadora')),
            ],
            options={
                'unique_together': {('jugadora', 'ano', 'categoria', 'division')},
            },
        ),
    ]
