from django.urls import path, include, re_path


from .views import * 
from jugadoras import views
from rest_framework import routers, permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = routers.DefaultRouter()
router.register(r"", JugadorasAnalisisView, 'jugadoras_analisis')


schema_view = get_schema_view(
   openapi.Info(
      title="Prueba Pucara API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="josefina_otero@hotmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
   
   
    path('<int:ano>/<categoria>/',  jugadoras_por_categoria_ano, name='jugadoras_por_categoria_ano'),
    path('categoria/', jugadoras_por_categoria, name='jugadoras_por_categoria'),
    path('prueba/', jugadoras_por_categoria1, name='jugadoras_por_categoria1'),
    
    path('seleccionar/', seleccionar_jugadoras, name='seleccionar_jugadoras'),
    path('registro/', registrar_jugadora, name='registrar_jugadora'),
    path('gestionar-jugadoras/', GestionarJugadorasPorAnoView.as_view(), name='gestionar_jugadoras'),
    path('guardar-jugadoras/', guardar_jugadoras, name='guardar_jugadoras'),

    path('lista/', urls_list, name='urls_list'),
    path('analisis/', AnalisisJugadoras, name='analisis_jugadoras'),
    path('editar-estado-jugadora/', editar_estado_jugadora, name='editar_estado_jugadora'),
    
    path('modificar-jugadora-categoria/', modificar_jugadora_categoria, name='modificar_jugadora_categoria'),
    path('detalle-jugadora/', detalle_jugadora, name='detalle_jugadora'),
    path('detalle-jugadora/autocomplete/', views.autocomplete_jugadoras, name='autocomplete_jugadoras'),
    
   #  path('api/categoria/', JugadorasPorCategoriaAPIView.as_view(), name='jugadoras_por_categoria_api'),
   #  path('api/<int:ano>/', JugadoraPorAnoAPIView.as_view(), name='jugadoras_por_ano'),
   #  path('api/lista/', JugadoraListAPIView.as_view(), name='lista'),
    
    
    path ("api/analisis/", include(router.urls)),    
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

