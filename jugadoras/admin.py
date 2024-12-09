from django import forms
from django.contrib import admin

from .forms import EstadoJugadoraForm
from .models import JugadoraPorAno, Jugadora, Categoria, Division, EstadoJugadora, Posicion, TiposEstado
# Register your models here.

class JugadoraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'fecha_nacimiento','dni', 'num_socia', 'activa')
    search_fields = ('nombre', 'apellido', 'dni', 'num_socia', )
    list_filter = ('activa', )
    
class JugadoraPorAnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugadora', 'ano', 'categoria', 'division')
    list_filter = ('ano', 'categoria', 'division', )
    search_fields = ('jugadora__nombre', 'jugadora__apellido', 'ano', )

class EstadoJugadoraAdmin(admin.ModelAdmin):
    form = EstadoJugadoraForm
    list_display = ('jugadora', 'fecha', 'estadoN', 'get_posiciones_display')
    list_filter = ('fecha', 'estadoN', )
    search_fields = ('jugadora__nombre', 'jugadora__apellido', 'fecha', )
    # Método para mostrar las posiciones en el list_display
    def get_posiciones_display(self, obj):
        return ", ".join([posicion.nombre for posicion in obj.posiciones.all()])
    get_posiciones_display.short_description = 'Posiciones'

class TiposEstadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

class PosicionAdmin(admin.ModelAdmin):
    list_display = ('nombre', )
    search_fields = ('nombre', )

admin.site.register(Jugadora, JugadoraAdmin)
admin.site.register(Categoria, admin.ModelAdmin)
admin.site.register(Division, admin.ModelAdmin)
admin.site.register(JugadoraPorAno, JugadoraPorAnoAdmin)
admin.site.register(EstadoJugadora, EstadoJugadoraAdmin)
admin.site.register(Posicion, PosicionAdmin)
admin.site.register(TiposEstado, TiposEstadoAdmin)