from django.urls import path
from . import views # Esto importa todas tus vistas de base/views.py
from django.contrib.auth.views import LogoutView

# Importa las vistas y la lista de formularios para el wizard desde views.py
from .views import RegistrationWizard, REGISTRATION_FORMS, registration_welcome

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # Tu vista raíz condicional

    # --- NUEVAS RUTAS PARA EL REGISTRO MULTIPASOS ---
    path('registro/bienvenida/', views.registration_welcome, name='registration_welcome'),
    path('registro/pasos/', RegistrationWizard.as_view(REGISTRATION_FORMS), name='registration_wizard'),

    # --- RUTAS EXISTENTES (se mantienen) ---
    path('registro-alimentacion/', views.registro_alimentacion, name='registro_alimentacion'),
    path('resumen/', views.resumen_diario, name='resumen_diario'),
    path('registros/', views.lista_registros, name='lista_registros'),
    path('registro/<int:pk>/eliminar/', views.eliminar_registro, name='eliminar_registro'),
    path('registro/<int:pk>/editar/', views.editar_registro, name='editar_registro'),
    path('sugerencias-alimentos/', views.sugerencias_alimentos, name='sugerencias_alimentos'),
    path('ejercicios/', views.ver_ejercicios, name='ver_ejercicios'),
    path('ejercicios/pecho/', views.vista_pecho, name='vista_pecho'),
    path('ejercicios/espalda/', views.vista_espalda, name='vista_espalda'),
    path('ejercicios/piernas/', views.vista_piernas, name='vista_piernas'),
    path('ejercicios/hombros/', views.vista_hombros, name='vista_hombros'),
    path('ejercicios/brazos/', views.vista_brazos, name='vista_brazos'),
    path('ejercicios/abdominales/', views.vista_abdominales, name='vista_abdominales'),
        
    # path('inicio/', views.inicio_publico, name='inicio_publico'), # ⬅️--- LÍNEA ELIMINADA/COMENTADA ---
]