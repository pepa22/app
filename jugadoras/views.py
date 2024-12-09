from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q ,Prefetch
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.urls import reverse
from .models import JugadoraPorAno, Jugadora, Categoria,  Division
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from .serializers import JugadoraSerializer, JugadoraPorAnoSerializer, CategoriaSerializer, JugadoraAnalisisSerializer

from .forms import * 
from django.db import transaction
import logging
from django.http import JsonResponse
from django.utils import timezone
import json

logger = logging.getLogger(__name__)

# Create your views here.

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('OK', schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
)
@api_view(['GET'])

@login_required
def jugadoras_por_categoria_ano(request, ano, categoria):
    # Buscar la categoría usando el nombre proporcionado
    categoria = get_object_or_404(Categoria, nombre=categoria)
    
    # Realizar la consulta filtrando por el año y la categoría obtenida
    jugadoras = JugadoraPorAno.objects.filter(ano=ano, categoria=categoria).select_related('jugadora', 'division')
    # Obtener el total de jugadoras para el año y categoría
    total_jugadoras = jugadoras.count()
    # Contexto para pasar a la plantilla
    context = {
        'jugadoras': jugadoras,
        'ano': ano,
        'categoria': categoria.nombre,
         
    }
    return render(request, 'jugadoras/jugadoras.html', context)

@login_required
def jugadoras_por_categoria(request):
    # Obtener todas las categorías
    categorias = Categoria.objects.all()
    
    
    # Obtener el año seleccionado del request, si no hay usar 2024 como valor predeterminado
    año_seleccionado = request.GET.get('año', 2024)
    
    # Obtener todos los años disponibles para referencia
    años_disponibles = JugadoraPorAno.objects.values_list('ano', flat=True).distinct().order_by('ano')
    
    # Filtrar jugadoras por el año seleccionado
    jugadoras_filtradas = JugadoraPorAno.objects.filter(ano=año_seleccionado)
    total_jugadoras_ano = jugadoras_filtradas.count()
    # Para cada categoría, obtener las jugadoras filtradas por año y agruparlas
    datos_por_categoria = []
    for categoria in categorias:
        if categoria.nombre == 'PS':
            # Lógica específica para PS
            antes_2000 = (
                jugadoras_filtradas.filter(
                    categoria=categoria,
                    jugadora__fecha_nacimiento__lt='2000-01-01'
                )
                .aggregate(cantidad=Count('jugadora'))['cantidad']
            )
            
            despues_2000 = (
                jugadoras_filtradas.filter(
                    categoria=categoria,
                    jugadora__fecha_nacimiento__gte='2000-01-01'
                )
                .aggregate(cantidad=Count('jugadora'))['cantidad']
            )

            jugadoras_agrupadas = [
                {'grupo': 'Nacidas antes del 2000', 'cantidad': antes_2000},
                {'grupo': 'Nacidas en o después del 2000', 'cantidad': despues_2000},
            ]
        else:
            # Agrupar jugadoras por año de nacimiento
            jugadoras = (
                jugadoras_filtradas.filter(categoria=categoria)
                .values('jugadora__fecha_nacimiento__year')
                .annotate(cantidad=Count('id'))
                .order_by('jugadora__fecha_nacimiento__year')
            )

            jugadoras_agrupadas = [
                {'grupo': jugadora['jugadora__fecha_nacimiento__year'], 'cantidad': jugadora['cantidad']}
                for jugadora in jugadoras
            ]
        
        
        total_jugadoras = sum(j['cantidad'] for j in jugadoras_agrupadas)
        datos_por_categoria.append({
            'categoria': categoria.nombre,
            'jugadoras': jugadoras_agrupadas,
            'total': total_jugadoras
        })

    context = {
        'datos_por_categoria': datos_por_categoria,
        'año_seleccionado': año_seleccionado,
        'años_disponibles': años_disponibles,
        'total_jugadoras_ano': total_jugadoras_ano,
        
    }

    return render(request, 'jugadoras/jugadoras_por_categoria.html', context)

@login_required
def seleccionar_jugadoras(request):
    # Inicializar los formularios
    filtro_form = FiltroJugadorasForm()
    seleccion_form = SeleccionForm()
    # Obtener los años y categorías disponibles para el filtro
    años_disponibles = JugadoraPorAno.objects.values_list('ano', flat=True).distinct().order_by('ano')
    # categorias = Categoria.objects.all()

    # Inicializar el queryset vacío para las jugadoras
    jugadoras = JugadoraPorAno.objects.none()

    # Si hay parámetros de filtro en la sesión, aplicarlos
    if 'filtro_ano' in request.session and 'filtro_categoria' in request.session:
        filtro_form = FiltroJugadorasForm(initial={
            'ano': request.session['filtro_ano'],
            'categoria': request.session['filtro_categoria']
        })
       
        # Obtener jugadoras según el filtro
        jugadoras = JugadoraPorAno.objects.filter(
            ano=request.session['filtro_ano'],
            categoria=request.session['filtro_categoria']
        ).select_related('jugadora')

        # Agrupar por año de nacimiento
        jugadoras = jugadoras.order_by('jugadora__fecha_nacimiento__year')
        
        # Actualizar el queryset del formulario de selección
        seleccion_form.fields['jugadoras'].queryset = jugadoras

    if request.method == 'POST':
        print("Método POST recibido")
        if 'aplicar_filtro' in request.POST:
            
            filtro_form = FiltroJugadorasForm(request.POST)
            if filtro_form.is_valid():
                ano_filtro = filtro_form.cleaned_data['ano']
                categoria_filtro = filtro_form.cleaned_data['categoria']
                
                jugadoras = JugadoraPorAno.objects.filter(
                    ano=ano_filtro,
                    categoria=categoria_filtro
                ).select_related('jugadora', 'categoria')
                
                seleccion_form = SeleccionForm()
                seleccion_form.fields['jugadoras'].queryset = jugadoras
                
                print(f"Filtro aplicado. Jugadoras encontradas: {jugadoras.count()}")
            else:
                print("Formulario de filtro no válido")
                print(filtro_form.errors)
        
        elif 'guardar_seleccion' in request.POST and request.POST['guardar_seleccion'] == 'guardar':
            print("POST data:", request.POST)  # Debug para ver qué datos llegan
            ano_seleccion = request.POST.get('ano_seleccion')
            if not ano_seleccion:
                messages.error(request, "Falta el año de destino.")
                return redirect('seleccionar_jugadoras')
            # Crear el formulario con TODOS los datos del POST
            
            seleccion_form = SeleccionForm(request.POST)
            
            # Asegurarnos que el campo año_seleccion está en el formulario
            if 'ano_seleccion' not in request.POST:
                messages.error(request, 'Falta el año de destino')
                return redirect('seleccionar_jugadoras')

            if seleccion_form.is_valid():
                ano_seleccion = seleccion_form.cleaned_data['ano_seleccion']
                categoria_seleccion = seleccion_form.cleaned_data['categoria']
                jugadoras_seleccionadas = seleccion_form.cleaned_data['jugadoras']
                
                print(f"Año seleccionado: {ano_seleccion}")
                print(f"Categoría seleccionada: {categoria_seleccion}")
                print("Jugadoras seleccionadas:")
                for jugadora in jugadoras_seleccionadas:
                    print(f"- {jugadora.jugadora.nombre} {jugadora.jugadora.apellido}")
                
                try:
                    with transaction.atomic():
                        nuevos_registros = []
                        for jugadora_actual in jugadoras_seleccionadas:
                            # Usar la división actual de la jugadora
                            division_actual = jugadora_actual.division
                            
                            # Crear nueva entrada para el año seleccionado manteniendo la división actual
                            JugadoraPorAno.objects.create(
                                jugadora=jugadora_actual.jugadora,
                                ano=ano_seleccion,
                                division=division_actual,  # Usar la división actual
                                categoria=categoria_seleccion
                            )
                        
                        if nuevos_registros:
                            print(nuevos_registros)
                            JugadoraPorAno.objects.bulk_create(nuevos_registros)
                            print(f"Se crearon {len(nuevos_registros)} nuevos registros")
                            messages.success(request, f'Se crearon {len(nuevos_registros)} nuevos registros para el año {ano_seleccion}')
                        else:
                            print("No se crearon nuevos registros")
                            messages.info(request, 'No se crearon nuevos registros, las jugadoras ya existían para el año seleccionado')
                        
                        return redirect('/jugadoras/seleccionar_jugadoras/')
                except Exception as e:
                    print(f"Error al procesar las selecciones: {str(e)}")
                    messages.error(request, f'Error al procesar las selecciones: {str(e)}')
                    logger.error(f"Error en seleccionar_jugadoras: {str(e)}", exc_info=True)
            else:
                print("Errores en el formulario:", seleccion_form.errors)
                messages.error(request, f'Errores en el formulario: {seleccion_form.errors}')

    # # Si hay parámetros GET, aplicar el filtro
    # elif request.GET:
    #     print("Procesando parámetros GET")
    #     filtro_form = FiltroJugadorasForm(request.GET)
    #     if filtro_form.is_valid():
    #         ano_filtro = filtro_form.cleaned_data['ano']
    #         categoria_filtro = filtro_form.cleaned_data['categoria']
            
    #         jugadoras = JugadoraPorAno.objects.filter(
    #             ano=ano_filtro,
    #             categoria=categoria_filtro
    #         ).select_related('jugadora', 'categoria', 'division')
            
    #         seleccion_form.fields['jugadoras'].queryset = jugadoras
    #         print(f"Filtro aplicado por GET. Jugadoras encontradas: {jugadoras.count()}")

    return render(request, 'jugadoras/seleccionar_jugadoras.html', {
        'filtro_form': filtro_form,
        'seleccion_form': seleccion_form,
        'divisiones': Division.objects.all(),
    })

@login_required
def registrar_jugadora(request):
    if request.method == 'POST':
        form = JugadoraForm(request.POST)
        if form.is_valid():
            try:
                datos = form.cleaned_data
                
                jugadora_por_socia = Jugadora.objects.filter(num_socia=datos['num_socia']).exclude(dni=datos['dni']).first()
                if jugadora_por_socia:
                    messages.error(request, 'Ya existe una jugadora con ese número de socia')
                    return render(request, 'jugadoras/registro_jugadora.html', {'form': form})

                jugadora = Jugadora.objects.filter(dni=datos['dni']).first()
                if jugadora:
                    # Actualizar datos de la jugadora existente
                    jugadora.nombre = datos['nombre']
                    jugadora.apellido = datos['apellido'] 
                    jugadora.fecha_nacimiento = datos['fecha_nacimiento']
                    jugadora.num_socia = datos['num_socia']
                    jugadora.save()
                    
                else:
                    # Crear nueva jugadora
                    nueva_jugadora = Jugadora.objects.create(
                        nombre=datos['nombre'],
                        apellido=datos['apellido'],
                        fecha_nacimiento=datos['fecha_nacimiento'],
                        dni=datos['dni'],
                        num_socia=datos['num_socia']
                    )
                    
                    # Crear registro JugadoraPorAno
                    JugadoraPorAno.objects.create(
                        jugadora=nueva_jugadora,
                        ano=datos['ano'],
                        categoria=datos['categoria'],
                        division=datos['division']
                    )
                    
                    messages.success(request, 'Nueva jugadora registrada correctamente')
                form = JugadoraForm()  # Crear un nuevo formulario en blanco
                return redirect('registrar_jugadora')
                
            except Exception as e:
                messages.error(request, f'Error al procesar el registro: {str(e)}')
                logger.error(f"Error en registrar_jugadora: {str(e)}", exc_info=True)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = JugadoraForm()
        filtro_form = FiltroJugadorasForm()
        seleccion_form = SeleccionForm()

    return render(request, 'jugadoras/registro_jugadora.html', {
        'form': form,
        'filtro_form': filtro_form,
        'seleccion_form': seleccion_form,
    })

@login_required            
def modificar_jugadora_categoria(request):
    """
    Vista para modificar la categoría y división de una jugadora.
    Permite actualizar estos campos en la base de datos.
    """
    # Obtener año del request sin valor predeterminado
    año_seleccionado = request.GET.get('año')
    categoria_seleccionada = request.GET.get('categoria')
    
    # Obtener datos para los filtros
    años_disponibles = JugadoraPorAno.objects.values_list('ano', flat=True).distinct().order_by('ano')
    categorias = Categoria.objects.all()
    # Verificar si ya existe una jugadora con la misma combinación de año y categoría
    def validar_jugadora_existente(jugadora_id, ano, categoria_id, division_id):
        return JugadoraPorAno.objects.filter(
            jugadora_id=jugadora_id,
            ano=ano,
            categoria_id=categoria_id, 
            division_id=division_id
        ).exists()
    # Filtrar jugadoras
    jugadoras = JugadoraPorAno.objects.filter(ano=año_seleccionado)
    
    if categoria_seleccionada:
        jugadoras = jugadoras.filter(categoria__nombre=categoria_seleccionada)
        jugadoras = jugadoras.order_by('jugadora__apellido')
    # Agrupar por división
    jugadoras_por_division = {}
    jugadoras_por_categoria = {}
    for jugadora in jugadoras:
        division = jugadora.division.nombre
        categoria = jugadora.categoria.nombre
        if division not in jugadoras_por_division:
            jugadoras_por_division[division] = []
        jugadoras_por_division[division].append(jugadora)
        if categoria not in jugadoras_por_categoria:
            jugadoras_por_categoria[categoria] = []
        jugadoras_por_categoria[categoria].append(jugadora)
    
    # Procesar cambios de división si hay POST
    if request.method == 'POST':
        jugadora_id = request.POST.get('jugadora_id')
        nueva_division_id = request.POST.get('nueva_division')
        nueva_categoria_id = request.POST.get('nueva_categoria')
        
        if jugadora_id:
            try:
                jugadora = JugadoraPorAno.objects.get(id=jugadora_id)
                
                # Actualizar división si se proporcionó
                if nueva_division_id:
                    nueva_division = Division.objects.get(id=nueva_division_id)
                    jugadora.division = nueva_division
                
                # Actualizar categoría si se proporcionó
                if nueva_categoria_id:
                    nueva_categoria = Categoria.objects.get(id=nueva_categoria_id)
                    jugadora.categoria = nueva_categoria
                
                jugadora.save()
                messages.success(request, 'Registro actualizado correctamente')
                return redirect(request.get_full_path())
                
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')

    # Obtener todas las divisiones para el selector
    divisiones = Division.objects.all()
    context = {
        'años_disponibles': años_disponibles,
        'año_seleccionado': año_seleccionado,
        'categorias': categorias,
        'divisiones': divisiones,
        'categoria_seleccionada': categoria_seleccionada,
        'jugadoras_por_division': jugadoras_por_division,
    }
    
    return render(request, 'jugadoras/modificar_jugadora_categoria.html', context)

#-------------------------------------------------------------------------------------------
#----Gestionar Jugadoras por Año-----------------------------------------------------------


class GestionarJugadorasPorAnoView(FormView):
    template_name = "gestionar_jugadoras.html"
    form_class = FiltroJugadorasForm1

    def form_valid(self, form):
        ano = form.cleaned_data['ano']
        categoria = form.cleaned_data['categoria']
        division = form.cleaned_data['division']
        jugadoras = form.cleaned_data['jugadoras']

        # Crear o actualizar registros en JugadoraPorAno
        for jugadora in jugadoras:
            registro, creado = JugadoraPorAno.objects.update_or_create(
                jugadora=jugadora,
                ano=ano,
                defaults={
                    'categoria': categoria,
                    'division': division,
                }
            )
        return redirect(reverse('jugadoras/gestionar_jugadoras'))  # Redirige después de guardar

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def jugadoras_por_categoria1(request):
    categorias = Categoria.objects.all()
    form = FiltroJugadorasForm1(request.GET or None)  # Procesar formulario si se envía

    jugadoras_filtradas = []  # Lista para almacenar jugadoras filtradas
    if form.is_valid():
        # Obtener los criterios del formulario
        categoria = form.cleaned_data['categoria']
        ano = form.cleaned_data['ano']

        
        # Realizar la consulta filtrando por el año y la categoría obtenida
        jugadoras_filtradas = JugadoraPorAno.objects.filter(ano=ano, categoria=categoria)
        # Ordenar jugadoras por apellido
        jugadoras_filtradas = jugadoras_filtradas.order_by('jugadora__apellido')

    
    context = {
            'categorias': categorias,
            'form': form,
        'jugadoras_filtradas': jugadoras_filtradas
        }
    
    return render(request, 'jugadoras/jugadoras_por_categoria1.html', context)




def guardar_jugadoras(request):
    if request.method == 'POST':
        seleccionadas = request.POST.getlist('jugadoras')
        
        # Obtener las jugadoras por año seleccionadas
        jugadoras_por_ano = JugadoraPorAno.objects.filter(id__in=seleccionadas)
        
        # Obtener los datos del formulario
        nuevo_ano = request.POST.get('nuevo_ano')
        #nueva_categoria = request.POST.get('categoria')
        # Verificar si ya existe un registro para la jugadora en el año destino
        for jpa in jugadoras_por_ano:
            existe_registro = JugadoraPorAno.objects.filter(
                jugadora=jpa.jugadora,
                ano=nuevo_ano if nuevo_ano else jpa.ano
            ).exists()
            
            if existe_registro:
                messages.error(request, f'La jugadora {jpa.jugadora.nombre} {jpa.jugadora.apellido} ya tiene un registro para el año {nuevo_ano}')
                continue
            else:
                # Verificar si la jugadora está activa
                if not jpa.jugadora.activa:
                    messages.error(request, f'La jugadora {jpa.jugadora.nombre} {jpa.jugadora.apellido} no está activa')
                    continue
                JugadoraPorAno.objects.update_or_create(
                    jugadora=jpa.jugadora,
                ano=nuevo_ano if nuevo_ano else jpa.ano,
                categoria=Categoria.objects.get(id=request.POST.get(f'categoria_{jpa.id}')),
                defaults={
                    'division': jpa.division  # Mantener la división original
                }
            )
        
        print("Jugadoras actualizadas:", jugadoras_por_ano)

        # Redirige después de guardar usando el nombre de la URL
        messages.success(request, 'Registro actualizado correctamente')
        return redirect('jugadoras_por_categoria1')  # Usar el nombre de la URL en lugar de la ruta
    
@login_required  
def detalle_jugadora(request):
    jugadora = None
    form = None
            
    if request.method == 'GET':
        nombre = request.GET.get('nombre')
        apellido = request.GET.get('apellido')
        
        if nombre or apellido:
            # Filtrar jugadoras por nombre y/o apellido
            jugadoras = Jugadora.objects.all()
            if nombre:
                jugadoras = jugadoras.filter(nombre__icontains=nombre)
            if apellido:
                jugadoras = jugadoras.filter(apellido__icontains=apellido)
            
            # Si hay exactamente una coincidencia, mostrar el detalle
            if jugadoras.count() == 1:
                jugadora = jugadoras.first()
                form = JugadoraDetalleForm(
                    initial={
                        'nombre': jugadora.nombre,
                        'apellido': jugadora.apellido,
                        'dni': jugadora.dni,
                        'fecha_nacimiento': jugadora.fecha_nacimiento,
                        'num_socia': jugadora.num_socia,
                        'activa': jugadora.activa
                    },
                    jugadora_id=jugadora.id
                )
            elif jugadoras.count() > 1:
                messages.warning(request, 'Se encontraron múltiples coincidencias. Por favor, sea más específico.')
            else:
                messages.warning(request, 'No se encontraron jugadoras con esos criterios.')
    
    context = {
        'form': form,
        'jugadora': jugadora
    }
    
    return render(request, 'jugadoras/detalle_jugadora.html', context)

def autocomplete_jugadoras(request):
    q = request.GET.get('q', '')
    field = request.GET.get('field')
    
    if not q:
        return JsonResponse([], safe=False)
    
    # Depuración: imprimir valores de entrada
    print(f"Término de búsqueda: {q}")
    print(f"Campo: {field}")
    
    if field == 'nombre':
        # Obtener nombres únicos que coincidan
        sugerencias = Jugadora.objects.filter(nombre__icontains=q).values_list('nombre', flat=True).distinct()
    elif field == 'apellido':
        # Obtener apellidos únicos que coincidan
        sugerencias = Jugadora.objects.filter(apellido__icontains=q).values_list('apellido', flat=True).distinct()
    else:
        sugerencias = []

    return JsonResponse(list(sugerencias), safe=False)

#-------------------------------------------------------------------------------------------
#----ANALISIS DE LAS JUGADORAS -------------------------------------------------------------

@login_required
def AnalisisJugadoras(request):
    form = FiltroCategoriaDivisionAnoForm(request.GET or None)
    jugadoras = []
    form_estado = EstadoJugadoraForm()
    posiciones = None
    estado_data = None

    if request.method == 'GET' and form.is_valid():
        # Filtrar jugadoras con estado prefetch
        ano = form.cleaned_data['ano']
        categoria = form.cleaned_data['categoria']
        division = form.cleaned_data['division']
        
        jugadoras = (
            JugadoraPorAno.objects.filter(ano=ano, categoria=categoria, division=division)
            .select_related('jugadora')
            .prefetch_related(Prefetch('estadojugadora_set', to_attr='estados'))
        )

        # Añadir el estado a cada jugadora
        for jugadora in jugadoras:
            jugadora.estado_jugadora = jugadora.estados[0] if jugadora.estados else None

        # Obtener posiciones y estados
        posiciones_response = agrupar_jugadoras_por_pos_estado(ano, categoria, division)
        if posiciones_response.status_code == 200:
            data = json.loads(posiciones_response.content)
            posiciones = data['data']['posiciones']
            estado_data = data['data']['estado']

    elif request.method == 'POST':
        jugadora_id = request.POST.get('jugadora_id')
        jugadora = get_object_or_404(JugadoraPorAno, id=jugadora_id)

        # Crear o actualizar el estado de la jugadora
        estado_jugadora, _ = EstadoJugadora.objects.get_or_create(
            jugadora=jugadora,
            defaults={'fecha': timezone.now()}
        )

        form_estado = EstadoJugadoraForm(request.POST, instance=estado_jugadora)
        if form_estado.is_valid():
            form_estado.save()
            return JsonResponse({'success': True, 'message': f'Estado de {jugadora.jugadora.nombre} actualizado correctamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form_estado.errors})

    context = {
        'form': form,
        'jugadoras': jugadoras,
        'form_estado': form_estado,
        'posiciones_data': posiciones,
        'estado_data': estado_data,
    }
    return render(request, 'jugadoras/analisis_jugadoras.html', context)


def agrupar_jugadoras_por_pos_estado(ano, categoria, division):
    """
    Agrupa jugadoras por posición y estado en función de los filtros.
    """
    jugadoras = (
        JugadoraPorAno.objects.filter(ano=ano, categoria=categoria, division=division)
        .select_related('jugadora')
    )

    estados = (
        EstadoJugadora.objects.filter(jugadora__in=jugadoras)
        .prefetch_related('posiciones', 'estadoN')
    )

    # Agrupar por posición y estado
    posiciones_count = {}
    estado_count = {}
    for estado in estados:
        # Agrupar posiciones
        for posicion in estado.posiciones.all():
            posiciones_count[posicion.nombre] = posiciones_count.get(posicion.nombre, 0) + 1
        # Agrupar estados
        if estado.estadoN:
            nombre_estado = estado.estadoN.nombre
            estado_count[nombre_estado] = estado_count.get(nombre_estado, 0) + 1

    return JsonResponse({
        'success': True,
        'data': {
            'ano': ano,
            'categoria': categoria.nombre,
            'division': division.nombre,
            'posiciones': posiciones_count,
            'estado': estado_count,
        },
    })
    
def editar_estado_jugadora(request):
    if request.method == 'POST':
        jugadora_id = request.POST.get('jugadora_id')
        jugadora = get_object_or_404(JugadoraPorAno, id=jugadora_id)

        estado_jugadora, _ = EstadoJugadora.objects.get_or_create(jugadora=jugadora)
        form = EstadoJugadoraForm(request.POST, instance=estado_jugadora)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Estado actualizado correctamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

# def AnalisisJugadoras(request):
#     form = FiltroCategoriaDivisionAnoForm(request.GET or None)
#     jugadoras = []
#     form_estado = None 

#     # Manejar el método GET
#     if request.method == 'GET' and form.is_valid():
#         ano = form.cleaned_data['ano']
#         categoria = form.cleaned_data['categoria']
#         division = form.cleaned_data['division']

#         # Filtrar jugadoras
#         jugadoras = JugadoraPorAno.objects.filter(
#             ano=ano, 
#             categoria=categoria, 
#             division=division
#         ).select_related('jugadora') 
#         # Obtener los estados de las jugadoras
#         estados_jugadoras = {}
#         for jugadora_por_ano in jugadoras:
#             try:
#                 estado = EstadoJugadora.objects.get(jugadora=jugadora_por_ano)
#                 print(estado)
#                 estados_jugadoras[jugadora_por_ano.id] = estado
#             except EstadoJugadora.DoesNotExist:
#                 estados_jugadoras[jugadora_por_ano.id] = None
                
#         # Agregar los estados al queryset de jugadoras
#         for jugadora in jugadoras:
#             jugadora.estado_jugadora = estados_jugadoras.get(jugadora.id)
#             print(jugadora.estado_jugadora)
      
#  # Manejar el método POST
#     elif request.method == 'POST':
#         jugadora_id = request.POST.get('jugadora_id')  # Nombre correcto del campo en el formulario
#         jugadora = get_object_or_404(JugadoraPorAno, id=jugadora_id)

#         # Crear o actualizar el estado de la jugadora
#         estado_jugadora, created = EstadoJugadora.objects.get_or_create(
#             jugadora=jugadora,
#             defaults={'fecha': timezone.now()}
#         )

#        # Procesar el formulario de estado
#         form_estado = EstadoJugadoraForm(request.POST, instance=estado_jugadora)
#         if form_estado.is_valid():
#             form_estado.save()
#             return JsonResponse({'success': True, 'message': f'Estado de {jugadora.jugadora.nombre} actualizado correctamente.'})
#         else:
#             return JsonResponse({'success': False, 'errors': form_estado.errors})
    
#     # Obtener datos de posiciones
#     posiciones = None
#     estado_data = None
    
#     if form.is_valid() and request.GET:
#         posiciones_response = agrupar_jugadoras_por_pos_estado(request)
#         if posiciones_response.status_code == 200:
#             posiciones_data = posiciones_response.content.decode()
#             data = json.loads(posiciones_data)
#             posiciones = data['data']['posiciones']
#             estado_data = data['data']['estado']
#             print(estado_data)

#     # Contexto final para el template
#     context = {
#         'form': form,
#         'jugadoras': jugadoras,
#         'form_estado': EstadoJugadoraForm(),
#         'posiciones_data': posiciones,
#         'estado_data': estado_data
#     }

#     return render(request, 'jugadoras/analisis_jugadoras.html', context)

# def agrupar_jugadoras_por_pos_estado(request):
#     form = FiltroCategoriaDivisionAnoForm(request.GET or None)
    
#     if form.is_valid():
#         ano = form.cleaned_data['ano']
#         categoria = form.cleaned_data['categoria'] 
#         division = form.cleaned_data['division']

#         # Obtener las jugadoras filtradas
#         jugadoras = JugadoraPorAno.objects.filter(
#             ano=ano,
#             categoria=categoria,
#             division=division
#         ).select_related('jugadora')

#         # Obtener los estados y posiciones
#         estados = EstadoJugadora.objects.filter(
#             jugadora__in=jugadoras
#         ).prefetch_related('posiciones', 'estadoN')
        
#         # Agrupar por posición
#         posiciones_count = {}
#         estado_count = {}
#         for estado in estados:
#             for posicion in estado.posiciones.all():
#                 if posicion.nombre in posiciones_count:
#                     posiciones_count[posicion.nombre] += 1
#                 else:
#                     posiciones_count[posicion.nombre] = 1
#         # Agrupar por estado
#         for estado in estados:
#             if estado.estadoN:
#                 nombre_estado = estado.estadoN.nombre
#                 if nombre_estado in estado_count:
#                     estado_count[nombre_estado] += 1
#                 else:
#                     estado_count[nombre_estado] = 1


#         return JsonResponse({
#             'success': True,
#             'data': {
#                 'ano': ano,
#                 'categoria': categoria.nombre,
#                 'division': division.nombre,
#                 'posiciones': posiciones_count,
#                 'estado': estado_count
#             }
#         })

#     return JsonResponse({
#         'success': False,
#         'errors': form.errors
#     })

#-------------------------------------------------------------------------------------------
#----API-------------------------------------------------------------

class JugadorasPorCategoriaAPIView(APIView):
    def get(self, request, format=None):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
    
# Listar todas las jugadoras con posibilidad de búsqueda por nombre y apellido
class JugadoraListAPIView(generics.ListAPIView):
    queryset = Jugadora.objects.all()
    serializer_class = JugadoraSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        nombre = self.request.query_params.get('nombre', None)
        apellido = self.request.query_params.get('apellido', None)
       

        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if apellido:
            queryset = queryset.filter(apellido__icontains=apellido)
        

        return queryset
    
# Agrupar jugadoras por categoría y división
class JugadoraPorCategoriaDivisionAPIView(APIView):
   
    
    @swagger_auto_schema(
        operation_description='descripcion de la operacion',
        operation_summary='resumen/titulo de la operacion',
        
       )
    def get(self, request, format=None):
        
        agrupacion = (
            JugadoraPorAno.objects
            .values('categoria__nombre', 'division__nombre')
            .annotate(cantidad=Count('jugadora__id'))
            .order_by('categoria__nombre', 'division__nombre')
        )

        return Response(agrupacion)
    
# Detalles por Año, Categoría, y División


class JugadoraPorAnoAPIView(generics.ListAPIView):
        
    serializer_class = JugadoraPorAnoSerializer
    
    @swagger_auto_schema(
        operation_description='descripcion de la operacion',
        operation_summary='resumen/titulo de la operacion',
       )
    def get_queryset(self):
        queryset = JugadoraPorAno.objects.all()
        ano = self.request.query_params.get('ano', None)
        categoria_id = self.request.query_params.get('categoria_id', None)
        division_id = self.request.query_params.get('division_id', None)

        if ano:
            queryset = queryset.filter(ano=ano)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if division_id:
            queryset = queryset.filter(division_id=division_id)

        return queryset
ano_param = openapi.Parameter('ano', openapi.IN_QUERY, description="Año en que juega", type=openapi.TYPE_INTEGER)
categoria_id_param = openapi.Parameter('categoria_id', openapi.IN_QUERY, description="ID de la categoría", type=openapi.TYPE_INTEGER)
division_id_param = openapi.Parameter('division_id', openapi.IN_QUERY, description="ID de la división", type=openapi.TYPE_INTEGER)
    
@swagger_auto_schema(
    manual_parameters=[ano_param, categoria_id_param, division_id_param],
            operation_summary='lista de jugadoras',
            operation_description = 'acceso a la lista de jugadoras por año, categoria y division')   

# class JugadorasAnalisisView(viewsets.ModelViewSet):
#         serializer_class = JugadoraAnalisisSerializer
        
#         queryset = JugadoraPorAno.objects.all()
        
class JugadorasAnalisisView(viewsets.ModelViewSet):
    serializer_class = JugadoraAnalisisSerializer
    queryset = JugadoraPorAno.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)  # Permitir múltiples registros
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        
        return Response(serializer.data)

def urls_list(request):
    return render(request, 'urls_list.html')


