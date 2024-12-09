from django.db import models
from django.utils import timezone
from django.utils.timezone import now
# Create your models here.


# now = timezone.now()
# print(now)
class Jugadora(models.Model):
   # id = models.IntegerField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=100, blank=True)
    apellido = models.CharField(max_length=100, blank=True)
    dni = models.IntegerField( unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(blank=True)
    num_socia = models.IntegerField( unique=True, null=True, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.apellido} ( {self.fecha_nacimiento.year} )"
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Division(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class JugadoraPorAno(models.Model):
    jugadora = models.ForeignKey(Jugadora, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    ano = models.IntegerField()
    

    class Meta:
        unique_together = ('jugadora', 'ano', 'categoria', 'division')

    def __str__(self):
        return  f"{self.jugadora.nombre}-{self.jugadora.apellido} -{self.ano}-{self.categoria.nombre}-{self.division.nombre}{self.jugadora.fecha_nacimiento}"
    
class Posicion(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class TiposEstado(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class EstadoJugadora(models.Model):
    # ESTADO_CHOICES = [
    #     ('JUEGA', 'Juega'),
    #     ('NO_JUEGA', 'No Juega'), 
    #     ('LESION', 'Lesionada'),
    #     ('OTROS', 'Otros')
    # ]

    jugadora = models.ForeignKey(JugadoraPorAno, on_delete=models.CASCADE)
    fecha = models.DateField(default=now) #definimos una fecha para hacer descripcion del estado de la jugadora
    estadoN = models.ForeignKey(TiposEstado, on_delete=models.CASCADE, null=True, blank=True)
    posiciones = models.ManyToManyField(Posicion, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.jugadora} - {self.fecha} - {self.estadoN}"

    class Meta:
        ordering = ['-fecha']
# class Seleccion(models.Model):
#     jugadora = models.ForeignKey(JugadoraPorAno, on_delete=models.CASCADE)
#     ano = models.PositiveIntegerField()