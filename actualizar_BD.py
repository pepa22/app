import pandas as pd
from django.core.management.base import BaseCommand
from jugadoras.models import Jugadora, Categoria, Division, JugadoraPorAno


df = pd.read_csv('src/csv/2024.csv', sep=';', encoding='latin1')



# a  = df.groupby('DNI').filter(lambda x: len(x) > 1).sort_values('DNI') 
#b  = df.groupby('NUM_SOC').filter(lambda x: len(x) > 1).sort_values('NUM_SOC')
#print(b)
for index, row in df.iterrows():
            categoria, created = Categoria.objects.get_or_create(nombre=row['CATEGORIA'])
            division, created = Division.objects.get_or_create(nombre=row['DIVISION'])
              # Verificar si el DNI y el número de socia están presentes, de lo contrario asignar None
            dni = row['DNI'] if pd.notna(row['DNI']) and row['DNI'] != '' else None
            num_socia = row['NUM_SOC'] if pd.notna(row['NUM_SOC']) and row['NUM_SOC'] != '' else None
            # defino formato de fecha
            print(row['NOMBRE'],'-', row['APELLIDO'])
            fecha = pd.to_datetime(row['FECHA'], errors='coerce', format='%d/%m/%Y')
#             #print(fecha)
            if (dni is None or dni == '0') and (num_socia is None or num_socia == '0'):
        # Si ambos son None o '0', saltar este registro
                continue
            jugadora, created = Jugadora.objects.get_or_create(
              #  id = index,
                dni=dni,
                defaults={
                    'nombre': row['NOMBRE'],
                    'apellido': row['APELLIDO'],
                    'num_socia': num_socia,
                    'activa': True if row['ACTIVAS'].strip().lower() == 'si' else False,
                    'fecha_nacimiento': fecha
                }
            )

            JugadoraPorAno.objects.create(
                jugadora=jugadora,
                categoria=categoria,
                division=division,
                ano=2024
            )

print('Jugadoras cargadas exitosamente!')
