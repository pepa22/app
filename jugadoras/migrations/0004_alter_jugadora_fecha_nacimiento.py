# Generated by Django 4.2.15 on 2024-08-30 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jugadoras', '0003_alter_jugadora_fecha_nacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jugadora',
            name='fecha_nacimiento',
            field=models.DateField(),
        ),
    ]