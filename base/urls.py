# base/urls.py

from django.urls import path
from . import views # Importa el módulo views completo
from django.contrib.auth.views import LoginView, LogoutView
from .forms import LoginForm
# Importa específicamente lo que necesitas del wizard desde views
# Asegúrate que estos nombres existan en tu base/views.py
from .views import RegistrationWizard, REGISTRATION_FORMS, registration_welcome

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Autenticación
    path('login/', LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='dashboard'), name='logout'),
    
    # Flujo de Registro con Wizard (AHORA ACTIVAS)
    path('registro/bienvenida/', views.registration_welcome, name='registration_welcome'),
    path('registro/pasos/', RegistrationWizard.as_view(REGISTRATION_FORMS), name='registration_wizard'),


    # Dashboard y Perfil
    path('mis-objetivos/', views.mis_objetivos, name='mis_objetivos'),
    path('registrar-medidas/', views.registrar_medidas, name='registrar_medidas'),
    path('perfil/', views.ver_perfil, name='ver_perfil'),

    # Alimentos
    path('alimentos/diario/', views.diario_alimentos, name='diario_alimentos_hoy'),
    path('alimentos/diario/<str:fecha_str>/', views.diario_alimentos, name='diario_alimentos_fecha'),
    path('alimentos/registro-bd/', views.registro_alimentacion, name='registro_alimentacion'), # Nombre que tenías para crear alimentos en BD
    path('alimentos/database/', views.buscar_alimento_db, name='alimentos_database'),
    path('alimentos/actualizar-agua/', views.actualizar_consumo_agua, name='actualizar_consumo_agua'),
    path('sugerencias-alimentos/', views.sugerencias_alimentos, name='sugerencias_alimentos'),
    path('registros/alimento/editar/<int:pk>/', views.editar_registro, name='editar_registro'),
    path('registros/alimento/eliminar/<int:pk>/', views.eliminar_registro, name='eliminar_registro'),

    # Ejercicios
    path('ejercicios/database/', views.database_ejercicios, name='database_ejercicios'),
    path('ejercicios/grupo/pecho/', views.vista_pecho, name='vista_pecho'),
    path('ejercicios/grupo/espalda/', views.vista_espalda, name='vista_espalda'),
    path('ejercicios/grupo/piernas/', views.vista_piernas, name='vista_piernas'),
    path('ejercicios/grupo/hombros/', views.vista_hombros, name='vista_hombros'),
    path('ejercicios/grupo/brazos/', views.vista_brazos, name='vista_brazos'),
    path('ejercicios/grupo/abdominales/', views.vista_abdominales, name='vista_abdominales'),
    path('ejercicios/grupo/cardio/', views.vista_cardio_general, name='vista_cardio_general'),
    path('sugerencias-ejercicios/', views.sugerencias_ejercicios, name='sugerencias_ejercicios'),
    
    path('ejercicios/registro/<str:fecha_str>/', views.ver_ejercicios, name='ver_ejercicios_fecha'),
    path('ejercicios/registro/', views.ver_ejercicios, name='ver_ejercicios'), # Esta después de la que tiene fecha_str
    path('ejercicios/registro_ejercicio/editar/<int:pk>/', views.editar_registro_ejercicio, name='editar_registro_ejercicio'),
    path('ejercicios/registro_ejercicio/eliminar/<int:pk>/', views.eliminar_registro_ejercicio, name='eliminar_registro_ejercicio'),

    # Informes
    path('informes/registros/', views.lista_registros, name='lista_registros'),
    path('resumen-diario/', views.resumen_diario, name='resumen_diario'),
]