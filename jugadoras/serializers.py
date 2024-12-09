from rest_framework import serializers
from django.db.models import Count
from .models import Jugadora, Categoria, Division, JugadoraPorAno

class JugadoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jugadora
        fields = ['id','nombre', 'apellido', 'dni', 'fecha_nacimiento', 'num_socia', 'activa']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'nombre']

class JugadoraPorAnoSerializer(serializers.ModelSerializer):
    jugadora = JugadoraSerializer()
    categoria = CategoriaSerializer()
    division = DivisionSerializer()

    class Meta:
        model = JugadoraPorAno
        fields = ['id', 'jugadora', 'categoria', 'division', 'ano']
        
    def get_jugadoras(self, obj):
        # Agrupa las jugadoras por el año de nacimiento
        if obj.nombre == 'PS':
            antes_2000 = obj.jugadoraporano_set.filter(jugadora__fecha_nacimiento__lt='2000-01-01').count()
            despues_2000 = obj.jugadoraporano_set.filter(jugadora__fecha_nacimiento__gte='2000-01-01').count()

            return [
                {'grupo': '<2000', 'cantidad': antes_2000},
                {'grupo': '>=2000', 'cantidad': despues_2000},
            ]
        else:
            return (
                obj.jugadoraporano_set.values('jugadora__fecha_nacimiento__year')
                .annotate(cantidad=Count('jugadora__id'))
                .order_by('jugadora__fecha_nacimiento__year')
            )

# class JugadoraAnalisisSerializer(serializers.ModelSerializer):
#     # jugadora = JugadoraSerializer()
#     # categoria = CategoriaSerializer()
#     # division = DivisionSerializer()

#     class Meta:
#         model = JugadoraPorAno
#         fields = '__all__'
        
class JugadoraAnalisisSerializer(serializers.ModelSerializer):
    jugadora = JugadoraSerializer()
    categoria = CategoriaSerializer()
    division = DivisionSerializer()

    class Meta:
        model = JugadoraPorAno
        fields = ['id', 'jugadora', 'categoria', 'division', 'ano']  # Asegúrate de incluir todos los campos necesarios

    def create(self, validated_data):
        jugadora_data = validated_data.pop('jugadora')
        categoria_data = validated_data.pop('categoria')
        division_data = validated_data.pop('division')
        
        # Crear o obtener instancias relacionadas
        jugadora, created = Jugadora.objects.get_or_create(**jugadora_data)
        categoria, created = Categoria.objects.get_or_create(**categoria_data)
        division, created = Division.objects.get_or_create(**division_data)

        # Crear la instancia de JugadoraPorAno
        return JugadoraPorAno.objects.create(jugadora=jugadora, categoria=categoria, division=division, **validated_data)

    def update(self, instance, validated_data):
        jugadora_data = validated_data.pop('jugadora')
        categoria_data = validated_data.pop('categoria')
        division_data = validated_data.pop('division')

        # Actualizar o crear instancias relacionadas
        for attr, value in jugadora_data.items():
            setattr(instance.jugadora, attr, value)
        instance.jugadora.save()

        for attr, value in categoria_data.items():
            setattr(instance.categoria, attr, value)
        instance.categoria.save()

        for attr, value in division_data.items():
            setattr(instance.division, attr, value)
        instance.division.save()

        instance.ano = validated_data.get('ano', instance.ano)
        instance.save()
        
        return instance