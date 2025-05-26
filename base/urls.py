from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('registro/', views.registro, name='registro'),
    path('registro-alimentacion/', views.registro_alimentacion, name='registro_alimentacion'),
    path('resumen/', views.resumen_diario, name='resumen_diario'),
    path('registros/', views.lista_registros, name='lista_registros'),
    path('registro/<int:pk>/eliminar/', views.eliminar_registro, name='eliminar_registro'),
    path('registro/<int:pk>/editar/', views.editar_registro, name='editar_registro'),
    path('sugerencias-alimentos/', views.sugerencias_alimentos, name='sugerencias_alimentos'),
]
