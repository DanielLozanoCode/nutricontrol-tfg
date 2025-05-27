import os
import json
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from formtools.wizard.views import SessionWizardView

from .forms import (
    LoginForm,
    RegistroAlimentacionForm,
    Paso0NombreForm,
    Paso1ObjetivosForm,
    Paso2DetallesFisicosForm,
    Paso3CredencialesForm
)
from .models import Alimento, RegistroAlimentacion, Usuario

# Vista dashboard condicional
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return render(request, 'inicio_publico.html')

# --- VISTAS DE LA APLICACIÓN PRINCIPAL ---
@login_required
def registro_alimentacion(request):
    if request.method == 'POST':
        form = RegistroAlimentacionForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['alimento_nombre']
            cantidad = form.cleaned_data['cantidad']
            try:
                alimento = Alimento.objects.get(nombre__iexact=nombre)
                RegistroAlimentacion.objects.create(
                    usuario=request.user,
                    alimento=alimento,
                    cantidad=cantidad
                )
                messages.success(request, 'Registro de alimentación guardado con éxito.')
                return redirect('dashboard')
            except Alimento.DoesNotExist:
                messages.error(request, 'Ese alimento no existe aún en la base de datos.')
                # Considerar devolver el form con el error para no perder datos
                # return render(request, 'register_food.html', {'form': form}) # Ejemplo
                return redirect('registro_alimentacion')
    else:
        form = RegistroAlimentacionForm()
    return render(request, 'register_food.html', {'form': form})

@login_required
def sugerencias_alimentos(request):
    q = request.GET.get('q','').strip().lower()
    data = [] # Placeholder: Implementar carga de foods.json o API
    # Ejemplo de carga de JSON (asegúrate que el archivo exista y tenga el formato correcto):
    # foods_json_path = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', 'foods.json')
    # try:
    #     with open(foods_json_path, encoding='utf-8') as f:
    #         all_food_data = json.load(f) # Asume que es una lista de dicts o strings
    #     # Filtrar data basado en q
    #     if isinstance(all_food_data, list) and all_food_data:
    #         if isinstance(all_food_data[0], dict):
    #             data = [item['nombre'] for item in all_food_data if q in item.get('nombre', '').lower()][:10]
    #         elif isinstance(all_food_data[0], str):
    #             data = [item for item in all_food_data if q in item.lower()][:10]
    # except FileNotFoundError:
    #     messages.warning(request, "Archivo de sugerencias de alimentos (foods.json) no encontrado.")
    # except json.JSONDecodeError:
    #     messages.error(request, "Error al leer el archivo de sugerencias de alimentos.")
    return JsonResponse(data, safe=False)

@login_required
def resumen_diario(request):
    hoy = date.today()
    registros = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=hoy)
    total_calorias = total_proteinas = total_grasas = total_carbohidratos = 0
    for r in registros:
        if r.alimento and r.cantidad is not None:
            factor = r.cantidad / 100
            total_calorias += (r.alimento.calorias or 0) * factor
            total_proteinas += (r.alimento.proteinas or 0) * factor
            total_grasas += (r.alimento.grasas or 0) * factor
            total_carbohidratos += (r.alimento.carbohidratos or 0) * factor
    context = {
        'registros': registros, 'fecha': hoy,
        'total_calorias': total_calorias, 'total_proteinas': total_proteinas,
        'total_grasas': total_grasas, 'total_carbohidratos': total_carbohidratos,
    }
    return render(request, 'resumen_diario.html', context)

@login_required
def lista_registros(request):
    registros = RegistroAlimentacion.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'registros.html', {'registros': registros})

@login_required
def eliminar_registro(request, pk):
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    registro_obj.delete()
    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('lista_registros')

@login_required
def editar_registro(request, pk):
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = RegistroAlimentacionForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['alimento_nombre']
            cantidad = form.cleaned_data['cantidad']
            try:
                alimento = Alimento.objects.get(nombre__iexact=nombre)
                registro_obj.alimento = alimento
                registro_obj.cantidad = cantidad
                registro_obj.save()
                messages.success(request, 'Registro actualizado correctamente.')
                return redirect('lista_registros')
            except Alimento.DoesNotExist:
                messages.error(request, 'Ese alimento no está en la base de datos.')
                # Para mantener los datos en el form tras error, puedes pasar request.POST de nuevo
                # form = RegistroAlimentacionForm(request.POST) # o simplemente no limpiar el form
    else:
        form = RegistroAlimentacionForm(initial={
            'alimento_nombre': registro_obj.alimento.nombre,
            'cantidad': registro_obj.cantidad,
        })
    return render(request, 'editar_registro.html', {'form': form, 'registro': registro_obj})

# --- VISTAS DE EJERCICIOS ---
@login_required
def ver_ejercicios(request):
    return render(request, 'ejercicios.html') # Asume botones estáticos en la plantilla

def cargar_ejercicios_por_grupo(nombre_archivo):
    ruta_completa = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', nombre_archivo)
    try:
        with open(ruta_completa, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"grupo": nombre_archivo.replace('.json','').capitalize(), "ejercicios": []}
    except json.JSONDecodeError:
        return {"grupo": nombre_archivo.replace('.json','').capitalize(), "ejercicios": [], "error": "JSON mal formado"}


@login_required
def vista_pecho(request):
    datos = cargar_ejercicios_por_grupo('pecho.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Pecho'), 'ejercicios': datos.get('ejercicios', [])})

@login_required
def vista_espalda(request):
    datos = cargar_ejercicios_por_grupo('espalda.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Espalda'), 'ejercicios': datos.get('ejercicios', [])})

@login_required
def vista_piernas(request):
    datos = cargar_ejercicios_por_grupo('piernas.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Piernas'), 'ejercicios': datos.get('ejercicios', [])})

@login_required
def vista_hombros(request):
    datos = cargar_ejercicios_por_grupo('hombros.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Hombros'), 'ejercicios': datos.get('ejercicios', [])})

@login_required
def vista_brazos(request):
    datos = cargar_ejercicios_por_grupo('brazos.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Brazos'), 'ejercicios': datos.get('ejercicios', [])})

@login_required
def vista_abdominales(request):
    datos = cargar_ejercicios_por_grupo('abdominales.json')
    return render(request, 'grupo_base.html', {'grupo': datos.get('grupo', 'Abdominales'), 'ejercicios': datos.get('ejercicios', [])})

# --- VISTAS PARA EL PROCESO DE REGISTRO MULTIPASOS ---
def registration_welcome(request):
    return render(request, 'registration_wizard/step_welcome.html')

REGISTRATION_FORMS = [
    ("nombre", Paso0NombreForm),
    ("objetivos", Paso1ObjetivosForm),
    ("detalles_fisicos", Paso2DetallesFisicosForm),
    ("credenciales", Paso3CredencialesForm),
]

REGISTRATION_TEMPLATES = {
    "nombre": "registration_wizard/step_nombre.html",
    "objetivos": "registration_wizard/step_objetivos.html",
    "detalles_fisicos": "registration_wizard/step_detalles_fisicos.html",
    "credenciales": "registration_wizard/step_credenciales.html",
}

class RegistrationWizard(SessionWizardView):
    form_list = REGISTRATION_FORMS
    
    def get_template_names(self):
        return [REGISTRATION_TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        try:
            user = Usuario.objects.create_user(
                username=form_data.get('username'),
                email=form_data.get('email'),
                password=form_data.get('password')
            )
            
            user.first_name = form_data.get('first_name', '')
            user.objetivo = form_data.get('objetivo')
            user.actividad_fisica = form_data.get('actividad_fisica')
            user.edad = form_data.get('edad')
            user.peso = form_data.get('peso')
            user.altura = form_data.get('altura')
            user.sexo = form_data.get('sexo')
            user.save()

            auth_login(self.request, user)
            messages.success(self.request, '¡Bienvenido a NutriControl! Tu cuenta ha sido creada y configurada exitosamente.')
            return redirect('dashboard')

        except Exception as e:
            print(f"Error en RegistrationWizard done: {e}") # Log para depuración
            messages.error(self.request, "Hubo un error inesperado al crear tu cuenta. Por favor, inténtalo de nuevo o contacta con el soporte.")
            return redirect('registration_welcome')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        
        current_step_name = self.steps.current # Nombre del paso actual (ej: "nombre", "objetivos")
        
        # Calcular porcentaje de progreso
        progress_percentage = (self.steps.step1 / self.steps.count) * 100
        context['progress_percentage'] = round(progress_percentage)
        
        # Define aquí los títulos y descripciones para cada paso.
        # Puedes internacionalizarlos directamente aquí con _() si lo prefieres.
        step_info = {
            "nombre": {
                "title": "Para empezar, ¿cómo te llamas?",
                "description": "Nos ayudará a personalizar tu experiencia en NutriControl."
            },
            "objetivos": {
                "title_base": "Ahora vamos con tus objetivos", # Usaremos este para construir el título personalizado
                "description": "Selecciona tu objetivo principal. Esto nos ayudará a enfocarnos."
            },
            "detalles_fisicos": {
                "title": "Algunos detalles sobre ti",
                "description": "Esta información nos ayuda a calcular tus necesidades y personalizar tu plan."
            },
            "credenciales": {
                "title": "Crea tus credenciales de acceso",
                "description": "Elige un nombre de usuario y una contraseña segura para tu cuenta NutriControl."
            },
        }

        # Título y descripción por defecto
        default_title = f"Registro - Paso {self.steps.step1}"
        step_title_to_display = step_info.get(current_step_name, {}).get('title', default_title)
        step_description_to_display = step_info.get(current_step_name, {}).get('description', "")
        
        # Personalizar el título del paso de "objetivos" con el nombre del usuario
        if current_step_name == 'objetivos':
            user_name_from_previous_step = None
            # 'nombre' es la clave que le dimos al Paso0NombreForm en la lista REGISTRATION_FORMS
            cleaned_data_nombre_step = self.get_cleaned_data_for_step('nombre') 
            if cleaned_data_nombre_step: # Asegurarse que hay datos del paso anterior
                user_name_from_previous_step = cleaned_data_nombre_step.get('first_name')
            
            # Usar el título base definido en step_info para "objetivos"
            objetivos_base_title = step_info.get("objetivos", {}).get("title_base", "Ahora vamos con tus objetivos")
            if user_name_from_previous_step:
                step_title_to_display = f"¡Gracias, {user_name_from_previous_step}! {objetivos_base_title.lower()}"
            else: # Fallback si el nombre no se encontró por alguna razón
                 step_title_to_display = f"¡Gracias! {objetivos_base_title.lower()}"
        
        context['step_title_from_view'] = step_title_to_display
        context['step_description_from_view'] = step_description_to_display
        
        return context