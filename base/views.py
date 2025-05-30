# base/views.py

import os
import json
from datetime import date, timedelta
from django.utils import timezone 
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login 
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from formtools.wizard.views import SessionWizardView

from .forms import (
    LoginForm,
    # RegistroAlimentacionForm, # Comentado ya que ahora usamos CrearAlimentoForm para esta URL/vista
    CrearAlimentoForm,      # <--- NUEVO FORMULARIO IMPORTADO
    MedidaCorporalForm, 
    Paso0NombreForm,
    Paso1ObjetivosForm,
    Paso2DetallesFisicosForm,
    Paso3CredencialesForm
)
from .models import Alimento, RegistroAlimentacion, Usuario, MedidaCorporal, ConsumoAgua


# Vista dashboard condicional
def dashboard(request):
    if request.user.is_authenticated:
        hoy = timezone.localdate()
        calorias_objetivo_usuario = getattr(request.user, 'calorias_objetivo_fijadas', 2200) 
        objetivo_proteinas_g_usuario = getattr(request.user, 'proteinas_objetivo_g', 150)
        objetivo_grasas_g_usuario = getattr(request.user, 'grasas_objetivo_g', 60)
        objetivo_carbohidratos_g_usuario = getattr(request.user, 'carbohidratos_objetivo_g', 265)
        registros_hoy = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=hoy)
        calorias_consumidas_hoy = 0; consumo_proteinas_g_hoy = 0; consumo_grasas_g_hoy = 0; consumo_carbohidratos_g_hoy = 0
        for r in registros_hoy:
            if r.alimento and r.cantidad is not None:
                calorias_consumidas_hoy += r.calorias_consumidas
                consumo_proteinas_g_hoy += r.proteinas_consumidas
                consumo_grasas_g_hoy += r.grasas_consumidas
                consumo_carbohidratos_g_hoy += r.carbohidratos_consumidos
        calorias_ejercicio_hoy = getattr(request.user, 'calorias_ejercicio_hoy_registradas', 0) 
        calorias_restantes_hoy = calorias_objetivo_usuario - calorias_consumidas_hoy + calorias_ejercicio_hoy
        porcentaje_carbohidratos_hoy = round((consumo_carbohidratos_g_hoy / objetivo_carbohidratos_g_usuario * 100) if objetivo_carbohidratos_g_usuario > 0 else 0)
        porcentaje_grasas_hoy = round((consumo_grasas_g_hoy / objetivo_grasas_g_usuario * 100) if objetivo_grasas_g_usuario > 0 else 0)
        porcentaje_proteinas_hoy = round((consumo_proteinas_g_hoy / objetivo_proteinas_g_usuario * 100) if objetivo_proteinas_g_usuario > 0 else 0)
        context = {
            'fecha_hoy_str': hoy.isoformat(), 'fecha_hoy': hoy,
            'calorias_objetivo': calorias_objetivo_usuario, 'calorias_consumidas': calorias_consumidas_hoy,
            'calorias_ejercicio': calorias_ejercicio_hoy, 'calorias_restantes': calorias_restantes_hoy,
            'objetivo_carbohidratos': objetivo_carbohidratos_g_usuario, 'consumo_carbohidratos': consumo_carbohidratos_g_hoy,
            'porcentaje_carbohidratos': min(porcentaje_carbohidratos_hoy, 100),
            'objetivo_grasas': objetivo_grasas_g_usuario, 'consumo_grasas': consumo_grasas_g_hoy,
            'porcentaje_grasas': min(porcentaje_grasas_hoy, 100),
            'objetivo_proteinas': objetivo_proteinas_g_usuario, 'consumo_proteinas': consumo_proteinas_g_hoy,
            'porcentaje_proteinas': min(porcentaje_proteinas_hoy, 100),
            'active_section': 'dashboard', 'active_subsection': 'dashboard_inicio' 
        }
        return render(request, 'dashboard.html', context)
    else:
        return render(request, 'inicio_publico.html')

@login_required
def mis_objetivos(request):
    # ... (código de mis_objetivos como estaba) ...
    calorias_objetivo_diario = getattr(request.user, 'calorias_objetivo_fijadas', 2200)
    objetivo_proteinas_g = getattr(request.user, 'proteinas_objetivo_g', 150) 
    objetivo_grasas_g = getattr(request.user, 'grasas_objetivo_g', 60)
    objetivo_carbohidratos_g = getattr(request.user, 'carbohidratos_objetivo_g', 265)
    porcentaje_proteinas = round((objetivo_proteinas_g * 4 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    porcentaje_grasas = round((objetivo_grasas_g * 9 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    porcentaje_carbohidratos = round((objetivo_carbohidratos_g * 4 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    cal_desayuno = calorias_objetivo_diario * 0.20; cal_almuerzo = calorias_objetivo_diario * 0.30; cal_cena = calorias_objetivo_diario * 0.30; cal_snacks = calorias_objetivo_diario * 0.20
    minutos_ejercicio_semana = getattr(request.user, 'minutos_ejercicio_obj', 150)
    entrenamientos_semana = getattr(request.user, 'entrenamientos_semana_obj', 3)
    calorias_quemadas_semana_obj = getattr(request.user, 'calorias_ejercicio_semana_obj', 1000)
    context = {
        'calorias_objetivo_diario': calorias_objetivo_diario,
        'objetivo_proteinas_g': objetivo_proteinas_g, 'porcentaje_proteinas': porcentaje_proteinas,
        'objetivo_grasas_g': objetivo_grasas_g, 'porcentaje_grasas': porcentaje_grasas,
        'objetivo_carbohidratos_g': objetivo_carbohidratos_g, 'porcentaje_carbohidratos': porcentaje_carbohidratos,
        'cal_desayuno': cal_desayuno, 'cal_almuerzo': cal_almuerzo, 'cal_cena': cal_cena, 'cal_snacks': cal_snacks,
        'minutos_ejercicio_semana': minutos_ejercicio_semana, 'entrenamientos_semana': entrenamientos_semana,
        'calorias_quemadas_semana_obj': calorias_quemadas_semana_obj,
        'active_section': 'dashboard', 'active_subsection': 'mis_objetivos' 
    }
    return render(request, 'objetivos.html', context)

@login_required
def registrar_medidas(request):
    # ... (código de registrar_medidas como estaba) ...
    today = timezone.localdate()
    medida_hoy_instancia = MedidaCorporal.objects.filter(usuario=request.user, fecha=today).first()
    if request.method == 'POST':
        form = MedidaCorporalForm(request.POST, instance=medida_hoy_instancia)
        if form.is_valid():
            medida = form.save(commit=False); medida.usuario = request.user; medida.fecha = today; medida.save()
            if medida.peso is not None: request.user.peso = medida.peso; request.user.save(update_fields=['peso'])
            messages.success(request, _('¡Medidas guardadas correctamente para hoy!'))
            return redirect('registrar_medidas') 
    else:
        initial_data = {}; 
        if not medida_hoy_instancia and hasattr(request.user, 'peso') and request.user.peso: initial_data['peso'] = request.user.peso
        form = MedidaCorporalForm(instance=medida_hoy_instancia, initial=initial_data if not medida_hoy_instancia and initial_data else None)
    context = {
        'form': form, 'fecha_hoy': today,
        'medida_registrada_hoy': MedidaCorporal.objects.filter(usuario=request.user, fecha=today).first(),
        'active_section': 'dashboard', 'active_subsection': 'registrar_medidas' 
    }
    return render(request, 'registrar_medidas.html', context)

@login_required
def ver_perfil(request):
    # ... (código de ver_perfil como estaba) ...
    usuario = request.user 
    ultimas_medidas = MedidaCorporal.objects.filter(usuario=usuario).order_by('-fecha').first()
    context = {
        'usuario_perfil': usuario, 'ultimas_medidas': ultimas_medidas, 
        'active_section': 'dashboard', 'active_subsection': 'ver_perfil' 
    }
    return render(request, 'perfil.html', context)

@login_required
def diario_alimentos(request, fecha_str=None):
    # ... (código de diario_alimentos como estaba en la última versión funcional) ...
    if fecha_str:
        try: fecha_seleccionada = date.fromisoformat(fecha_str)
        except ValueError: messages.error(request, _("Formato de fecha inválido.")); return redirect(reverse('diario_alimentos_hoy')) 
    else: fecha_seleccionada = timezone.localdate()
    dia_anterior = fecha_seleccionada - timedelta(days=1); dia_siguiente = fecha_seleccionada + timedelta(days=1)
    es_hoy = (fecha_seleccionada == timezone.localdate())
    registros_del_dia = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=fecha_seleccionada).order_by('fecha_creacion') 
    tipo_comida_display_dict = dict(RegistroAlimentacion.TIPO_COMIDA_CHOICES)
    tipos_comida_orden = [choice[0] for choice in RegistroAlimentacion.TIPO_COMIDA_CHOICES]
    _temp_comidas_data = { tipo: {'registros': [], 'total_calorias': 0} for tipo in tipos_comida_orden }
    for registro in registros_del_dia:
        if registro.tipo_comida and registro.tipo_comida in _temp_comidas_data:
            _temp_comidas_data[registro.tipo_comida]['registros'].append(registro)
            _temp_comidas_data[registro.tipo_comida]['total_calorias'] += registro.calorias_consumidas
    comidas_del_dia_lista_ordenada = []
    for tipo_key in tipos_comida_orden:
        data = _temp_comidas_data.get(tipo_key)
        if data: comidas_del_dia_lista_ordenada.append({'key': tipo_key, 'nombre_display': tipo_comida_display_dict.get(tipo_key, tipo_key.capitalize()), 'registros': data['registros'], 'total_calorias': data['total_calorias']})
    total_calorias_consumidas = sum(c['total_calorias'] for c in comidas_del_dia_lista_ordenada)
    total_proteinas_consumidas = sum(r.proteinas_consumidas for r in registros_del_dia if r.alimento); total_grasas_consumidas = sum(r.grasas_consumidas for r in registros_del_dia if r.alimento); total_carbohidratos_consumidos = sum(r.carbohidratos_consumidos for r in registros_del_dia if r.alimento)
    calorias_objetivo = getattr(request.user, 'calorias_objetivo_fijadas', 2000); objetivo_proteinas = getattr(request.user, 'proteinas_objetivo_g', 120); objetivo_grasas = getattr(request.user, 'grasas_objetivo_g', 60); objetivo_carbohidratos = getattr(request.user, 'carbohidratos_objetivo_g', 250)
    objetivo_usuario_actual = getattr(request.user, 'objetivo', 'man'); calorias_objetivo_ajustado = calorias_objetivo
    if objetivo_usuario_actual == 'vol': calorias_objetivo_ajustado += 300
    elif objetivo_usuario_actual == 'def': calorias_objetivo_ajustado -= 300
    elif objetivo_usuario_actual == 'res': calorias_objetivo_ajustado += 100
    calorias_ejercicio_registradas = getattr(request.user, 'calorias_ejercicio_hoy_registradas', 0)
    calorias_restantes = calorias_objetivo_ajustado - total_calorias_consumidas + calorias_ejercicio_registradas
    proteinas_restantes = objetivo_proteinas - total_proteinas_consumidas; grasas_restantes = objetivo_grasas - total_grasas_consumidas; carbohidratos_restantes = objetivo_carbohidratos - total_carbohidratos_consumidos
    consumo_agua_hoy, created = ConsumoAgua.objects.get_or_create(usuario=request.user, fecha=fecha_seleccionada, defaults={'cantidad_ml': 0})
    objetivo_agua_ml = 2000; porcentaje_agua = round((consumo_agua_hoy.cantidad_ml / objetivo_agua_ml * 100) if objetivo_agua_ml > 0 else 0)
    context = {
        'fecha_seleccionada_str': fecha_seleccionada.isoformat(), 'fecha_seleccionada_display': fecha_seleccionada,
        'dia_anterior_str': dia_anterior.isoformat(), 'dia_siguiente_str': dia_siguiente.isoformat(), 'es_hoy': es_hoy,
        'comidas_del_dia_lista_ordenada': comidas_del_dia_lista_ordenada,
        'total_calorias_consumidas': total_calorias_consumidas, 'total_proteinas_consumidas': total_proteinas_consumidas,
        'total_grasas_consumidas': total_grasas_consumidas, 'total_carbohidratos_consumidos': total_carbohidratos_consumidos,
        'calorias_objetivo_diario': calorias_objetivo_ajustado, 'objetivo_proteinas_g': objetivo_proteinas, 
        'objetivo_grasas_g': objetivo_grasas, 'objetivo_carbohidratos_g': objetivo_carbohidratos,
        'calorias_restantes': calorias_restantes, 'proteinas_restantes': proteinas_restantes,
        'grasas_restantes': grasas_restantes, 'carbohidratos_restantes': carbohidratos_restantes,
        'consumo_agua_ml': consumo_agua_hoy.cantidad_ml, 'objetivo_agua_ml': objetivo_agua_ml,
        'porcentaje_agua_consumida': min(porcentaje_agua, 100),
        'active_section': 'alimentos', 'active_subsection': 'diario_alimentos'
    }
    return render(request, 'diario_alimentos.html', context)

@login_required
def actualizar_consumo_agua(request):
    # ... (código de actualizar_consumo_agua como estaba) ...
    if request.method == 'POST':
        try:
            data = json.loads(request.body); fecha_str = data.get('fecha'); cantidad_ml_registrar = int(data.get('cantidad_ml', 0))
            if not fecha_str: return JsonResponse({'status': 'error', 'message': _('Fecha no proporcionada.')}, status=400)
            fecha_obj = date.fromisoformat(fecha_str)
            consumo_agua, created = ConsumoAgua.objects.get_or_create(usuario=request.user, fecha=fecha_obj, defaults={'cantidad_ml': 0})
            if cantidad_ml_registrar == -1: consumo_agua.cantidad_ml = 0
            elif cantidad_ml_registrar > 0 : consumo_agua.cantidad_ml += cantidad_ml_registrar
            consumo_agua.save()
            objetivo_agua_ml = 2000; porcentaje_agua = round((consumo_agua.cantidad_ml / objetivo_agua_ml * 100) if objetivo_agua_ml > 0 else 0)
            return JsonResponse({'status': 'ok', 'nueva_cantidad_ml': consumo_agua.cantidad_ml, 'porcentaje_agua': min(porcentaje_agua, 100)})
        except json.JSONDecodeError: return JsonResponse({'status': 'error', 'message': _('Datos JSON inválidos')}, status=400)
        except ValueError: return JsonResponse({'status': 'error', 'message': _('Formato de datos inválido')}, status=400)
        except Exception as e: return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': _('Solo se permiten peticiones POST')}, status=405)

@login_required
def buscar_alimento_db(request):
    # ... (código de buscar_alimento_db como estaba) ...
    query = request.GET.get('q_alimento', '')
    resultados = []
    if query:
        resultados = Alimento.objects.filter(nombre__icontains=query)
    context = {
        'resultados_busqueda': resultados, 'termino_busqueda': query,
        'active_section': 'alimentos', 'active_subsection': 'alimentos_database'
    }
    return render(request, 'alimentos_database.html', context)

# --- VISTA registro_alimentacion MODIFICADA PARA CREAR ALIMENTOS ---
@login_required
def registro_alimentacion(request): 
    if request.method == 'POST':
        form = CrearAlimentoForm(request.POST) # Usar el nuevo formulario
        if form.is_valid():
            try:
                form.save() # Guardar el nuevo alimento en la base de datos
                messages.success(request, _('Alimento "{}" añadido a la base de datos con éxito.').format(form.cleaned_data.get('nombre')))
                # Redirigir a la base de datos de alimentos o a la misma página para añadir otro
                return redirect('alimentos_database') # O 'registro_alimentacion' para añadir otro
            except Exception as e: # Capturar errores de guardado, como nombre duplicado si es unique
                print(f"Error al guardar alimento: {e}") # Log del error
                messages.error(request, _('No se pudo añadir el alimento. Es posible que ya exista un alimento con ese nombre.'))
                # Volver a mostrar el formulario con los datos y el error (si el form lo maneja)
                # form = CrearAlimentoForm(request.POST) # Esto ya se hizo
    else:
        form = CrearAlimentoForm()
    
    context = { 
        'form': form, 
        'active_section': 'alimentos',
        'active_subsection': 'registro_alimentacion' # Para marcar el enlace "Registrar Alimento" como activo
    }
    return render(request, 'register_food.html', context) # Usará tu plantilla register_food.html

# ... (Resto de tus vistas: sugerencias_alimentos, resumen_diario, lista_registros, etc.
#      y el RegistrationWizard, como los tenías en la última versión completa que te di) ...
# (He incluido todas las vistas que me pasaste en tu penúltimo mensaje, con los ajustes de active_section)
@login_required
def sugerencias_alimentos(request):
    # Esta vista ya no se usará con el nuevo propósito de register_food.html
    # pero la dejo por si la reutilizas para el diario.
    q = request.GET.get('q','').strip().lower()
    data = [] 
    if q:
        alimentos_sugeridos = Alimento.objects.filter(nombre__icontains=q).values_list('nombre', flat=True)[:10]
        data = list(alimentos_sugeridos)
    return JsonResponse(data, safe=False)

@login_required
def resumen_diario(request):
    hoy = timezone.localdate(); registros = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=hoy)
    total_calorias = 0; total_proteinas = 0; total_grasas = 0; total_carbohidratos = 0
    for r in registros:
        if r.alimento and r.cantidad is not None:
            total_calorias += r.calorias_consumidas; total_proteinas += r.proteinas_consumidas
            total_grasas += r.grasas_consumidas; total_carbohidratos += r.carbohidratos_consumidos
    context = {
        'registros': registros, 'fecha': hoy, 'total_calorias': total_calorias, 'total_proteinas': total_proteinas,
        'total_grasas': total_grasas, 'total_carbohidratos': total_carbohidratos,
        'active_section': 'informes', 'active_subsection': 'resumen_diario' 
    }
    return render(request, 'resumen_diario.html', context)

@login_required
def lista_registros(request): 
    registros = RegistroAlimentacion.objects.filter(usuario=request.user).order_by('-fecha', '-id')
    context = { 'registros': registros, 'active_section': 'informes', 'active_subsection': 'lista_registros' }
    return render(request, 'registros.html', context)

@login_required
def eliminar_registro(request, pk):
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    fecha_registro = registro_obj.fecha.isoformat() 
    registro_obj.delete()
    messages.success(request, _('Registro eliminado correctamente.'))
    return redirect(reverse('diario_alimentos_fecha', args=[fecha_registro]))

@login_required
def editar_registro(request, pk):
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    fecha_registro_str = registro_obj.fecha.isoformat()
    
    # Usaremos el antiguo RegistroAlimentacionForm para editar un consumo existente
    # Este form espera 'alimento_nombre' y 'cantidad'.
    # Si quisieras editar el tipo_comida, el form necesitaría ese campo.
    # Por ahora, asumimos que solo editas el alimento (buscándolo) y la cantidad.
    
    # Necesitamos un formulario que NO sea ModelForm si 'alimento_nombre' es un CharField
    # y quieres buscar Alimento por ese nombre. O ajustar el ModelForm.
    # Reutilicemos la lógica de `registro_alimentacion` para el POST.
    if request.method == 'POST':
        # Este es un hack. Para editar bien, necesitarías un form que pueda tomar el nombre
        # y buscar el Alimento, o un selector de Alimento.
        # Vamos a asumir que el form de registro original sirve para el POST de edición también.
        form_data = request.POST.copy()
        form = RegistroAlimentacionForm(form_data) # Usamos el form que era para consumo
        if form.is_valid():
            nombre_alimento_editado = form.cleaned_data['alimento_nombre']
            cantidad_editada = form.cleaned_data['cantidad']
            # tipo_comida_editado = form.cleaned_data.get('tipo_comida', registro_obj.tipo_comida) # Si tuvieras el campo

            try:
                alimento_nuevo = Alimento.objects.get(nombre__iexact=nombre_alimento_editado)
                registro_obj.alimento = alimento_nuevo
                registro_obj.cantidad = cantidad_editada
                # registro_obj.tipo_comida = tipo_comida_editado # Si se edita
                registro_obj.save()
                messages.success(request, _('Registro actualizado con éxito.'))
                return redirect(reverse('diario_alimentos_fecha', args=[fecha_registro_str]))
            except Alimento.DoesNotExist:
                form.add_error('alimento_nombre', _('El alimento especificado no existe en la base de datos.'))
        # Si el form no es válido, se renderizará de nuevo con errores
    else:
        # Pre-llenar el formulario de edición. Usaremos RegistroAlimentacionForm para la estructura.
        form = RegistroAlimentacionForm(initial={
            'alimento_nombre': registro_obj.alimento.nombre,
            'cantidad': registro_obj.cantidad,
            # 'tipo_comida': registro_obj.tipo_comida # Si tuvieras este campo en el form
        })
        
    context = { 
        'form': form, 
        'registro': registro_obj, # Para saber qué se está editando
        'active_section': 'alimentos', # O informes, según desde dónde se acceda
        'fecha_para_registro': fecha_registro_str, 
        'tipo_comida_para_registro': registro_obj.tipo_comida
    }
    return render(request, 'editar_registro.html', context)


@login_required
def ver_ejercicios(request): 
    context = {'active_section': 'ejercicio', 'active_subsection': 'ver_ejercicios'}
    return render(request, 'ejercicios.html', context)

def cargar_ejercicios_por_grupo(nombre_archivo):
    ruta_completa = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', 'json', nombre_archivo)
    try:
        with open(ruta_completa, encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: print(f"ADVERTENCIA: Archivo JSON no encontrado en {ruta_completa}"); return {"grupo": nombre_archivo.replace('.json','').capitalize(), "ejercicios": []}
    except json.JSONDecodeError: print(f"ERROR: Archivo JSON mal formado: {ruta_completa}"); return {"grupo": nombre_archivo.replace('.json','').capitalize(), "ejercicios": [], "error": "JSON mal formado"}

@login_required
def vista_pecho(request):
    datos = cargar_ejercicios_por_grupo('pecho.json'); context = {'grupo': datos.get('grupo', _('Pecho')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)
@login_required
def vista_espalda(request):
    datos = cargar_ejercicios_por_grupo('espalda.json'); context = {'grupo': datos.get('grupo', _('Espalda')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)
@login_required
def vista_piernas(request):
    datos = cargar_ejercicios_por_grupo('piernas.json'); context = {'grupo': datos.get('grupo', _('Piernas')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)
@login_required
def vista_hombros(request):
    datos = cargar_ejercicios_por_grupo('hombros.json'); context = {'grupo': datos.get('grupo', _('Hombros')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)
@login_required
def vista_brazos(request):
    datos = cargar_ejercicios_por_grupo('brazos.json'); context = {'grupo': datos.get('grupo', _('Brazos')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)
@login_required
def vista_abdominales(request):
    datos = cargar_ejercicios_por_grupo('abdominales.json'); context = {'grupo': datos.get('grupo', _('Abdominales')), 'ejercicios': datos.get('ejercicios',[]), 'active_section': 'ejercicio'}; return render(request, 'grupo_base.html', context)

def registration_welcome(request):
    return render(request, 'registration_wizard/step_welcome.html')
REGISTRATION_FORMS = [
    ("nombre", Paso0NombreForm), ("objetivos", Paso1ObjetivosForm),
    ("detalles_fisicos", Paso2DetallesFisicosForm), ("credenciales", Paso3CredencialesForm),
]
REGISTRATION_TEMPLATES = {
    "nombre": "registration_wizard/step_nombre.html", "objetivos": "registration_wizard/step_objetivos.html",
    "detalles_fisicos": "registration_wizard/step_detalles_fisicos.html", "credenciales": "registration_wizard/step_credenciales.html",
}
class RegistrationWizard(SessionWizardView):
    form_list = REGISTRATION_FORMS
    def get_template_names(self): return [REGISTRATION_TEMPLATES[self.steps.current]]
    def done(self, form_list, **kwargs):
        form_data = {k: v for form in form_list for k, v in form.cleaned_data.items()}
        try:
            user = Usuario.objects.create_user(username=form_data.get('username'), email=form_data.get('email'), password=form_data.get('password'))
            user.first_name = form_data.get('first_name', ''); user.objetivo = form_data.get('objetivo'); user.actividad_fisica = form_data.get('actividad_fisica', '') 
            user.edad = form_data.get('edad'); user.peso = form_data.get('peso'); user.altura = form_data.get('altura'); user.sexo = form_data.get('sexo')
            user.save()
            auth_login(self.request, user)
            messages.success(self.request, _('¡Bienvenido a NutriControl! Tu cuenta ha sido creada y configurada exitosamente.'))
            return redirect('dashboard')
        except Exception as e:
            print(f"Error en RegistrationWizard done: {e}"); messages.error(self.request, _("Hubo un error inesperado al crear tu cuenta.")); return redirect('registration_welcome')
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs); current_step_name = self.steps.current
        context['progress_percentage'] = round((self.steps.step1 / self.steps.count) * 100)
        step_info = {
            "nombre": {"title": _("Para empezar, ¿cómo te llamas?"), "description": _("Nos ayudará a personalizar tu experiencia en NutriControl.")},
            "objetivos": {"title_base": _("Ahora vamos con tus objetivos"), "description": _("Selecciona tu objetivo principal. Esto nos ayudará a enfocarnos.")},
            "detalles_fisicos": {"title": _("Algunos detalles sobre ti"), "description": _("Esta información nos ayuda a calcular tus necesidades y personalizar tu plan.")},
            "credenciales": {"title": _("Crea tus credenciales de acceso"), "description": _("Elige un nombre de usuario y una contraseña segura.")}
        }
        default_title = _("Registro - Paso {}").format(self.steps.step1); step_title_to_display = step_info.get(current_step_name, {}).get('title', default_title)
        if current_step_name == 'objetivos':
            user_name_from_previous_step = self.get_cleaned_data_for_step('nombre').get('first_name') if self.get_cleaned_data_for_step('nombre') else None
            objetivos_base_title = step_info.get("objetivos", {}).get("title_base", _("Ahora vamos con tus objetivos"))
            step_title_to_display = f"¡Gracias, {user_name_from_previous_step}! {objetivos_base_title.lower()}" if user_name_from_previous_step else f"¡Gracias! {objetivos_base_title.lower()}"
        context['step_title_from_view'] = step_title_to_display
        context['step_description_from_view'] = step_info.get(current_step_name, {}).get('description', "")
        return context