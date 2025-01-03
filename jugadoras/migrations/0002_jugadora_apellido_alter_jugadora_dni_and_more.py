# Generated by Django 4.2.15 on 2024-08-30 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jugadora',
            name='apellido',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='jugadora',
            name='dni',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='jugadora',
            name='nombre',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='jugadora',
            name='num_socia',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
