# base/urls.py

from django.urls import path
from . import views 
from django.contrib.auth.views import LoginView, LogoutView

from .views import RegistrationWizard, REGISTRATION_FORMS, registration_welcome
from .forms import LoginForm 

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 

    path('login/', LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='dashboard'), name='logout'), 

    path('registro/bienvenida/', views.registration_welcome, name='registration_welcome'),
    path('registro/pasos/', RegistrationWizard.as_view(REGISTRATION_FORMS), name='registration_wizard'),

    path('mis-objetivos/', views.mis_objetivos, name='mis_objetivos'),
    path('registrar-medidas/', views.registrar_medidas, name='registrar_medidas'), 
    path('perfil/', views.ver_perfil, name='ver_perfil'), 

    # --- SECCIÓN ALIMENTOS ---
    path('alimentos/diario/', views.diario_alimentos, name='diario_alimentos_hoy'), 
    path('alimentos/diario/<str:fecha_str>/', views.diario_alimentos, name='diario_alimentos_fecha'), 
    path('alimentos/registro/', views.registro_alimentacion, name='registro_alimentacion'), 
    path('alimentos/database/', views.buscar_alimento_db, name='alimentos_database'), # <--- NUEVA RUTA
    path('alimentos/actualizar-agua/', views.actualizar_consumo_agua, name='actualizar_consumo_agua'),

    path('ejercicios/', views.ver_ejercicios, name='ver_ejercicios'), 
    # path('ejercicios/database/', views.buscar_ejercicio_db, name='ejercicios_database'), # Placeholder
    path('ejercicios/pecho/', views.vista_pecho, name='vista_pecho'),
    path('ejercicios/espalda/', views.vista_espalda, name='vista_espalda'),
    path('ejercicios/piernas/', views.vista_piernas, name='vista_piernas'),
    path('ejercicios/hombros/', views.vista_hombros, name='vista_hombros'),
    path('ejercicios/brazos/', views.vista_brazos, name='vista_brazos'),
    path('ejercicios/abdominales/', views.vista_abdominales, name='vista_abdominales'),
    
    path('informes/registros/', views.lista_registros, name='lista_registros'), 
    # path('informes/resumen-semanal/', views.resumen_semanal_informes, name='informes_resumen_semanal'), # Placeholder
    
    path('resumen-diario/', views.resumen_diario, name='resumen_diario'), 
    path('registros/editar/<int:pk>/', views.editar_registro, name='editar_registro'), 
    path('registros/eliminar/<int:pk>/', views.eliminar_registro, name='eliminar_registro'), 
    path('sugerencias-alimentos/', views.sugerencias_alimentos, name='sugerencias_alimentos'),
]