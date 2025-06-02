# base/views.py

import os
import json
from datetime import date, timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login # Renombrado para evitar conflicto con la vista de login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from formtools.wizard.views import SessionWizardView

from .forms import (
    LoginForm,
    CrearAlimentoForm,
    MedidaCorporalForm,
    Paso0NombreForm,
    Paso1ObjetivosForm,
    Paso2DetallesFisicosForm,
    Paso3CredencialesForm,
    AnadirConsumoAlimentoForm,
    RegistrarEjercicioCardioForm,
    RegistrarEjercicioFuerzaForm,
    NotaDiariaEjercicioForm
)
from .models import (
    Alimento,
    RegistroAlimentacion,
    Usuario,
    MedidaCorporal,
    ConsumoAgua,
    Ejercicio,
    RegistroEjercicioRealizado,
    NotaDiariaEjercicio
)
# Importar la función de cálculo si está en un archivo separado, ej. calculations.py
from .calculations import calcular_calorias_objetivo_ingesta


# Vista dashboard condicional
def dashboard(request):
    if request.user.is_authenticated:
        hoy = timezone.localdate()
        # Lógica para usuarios autenticados (dashboard)
        calorias_objetivo_usuario = getattr(request.user, 'calorias_objetivo_fijadas', 2200)
        objetivo_proteinas_g_usuario = getattr(request.user, 'proteinas_objetivo_g', 150)
        objetivo_grasas_g_usuario = getattr(request.user, 'grasas_objetivo_g', 60)
        objetivo_carbohidratos_g_usuario = getattr(request.user, 'carbohidratos_objetivo_g', 265)
        registros_hoy = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=hoy)
        calorias_consumidas_hoy = sum(r.calorias_consumidas for r in registros_hoy if r.alimento and r.cantidad is not None)
        consumo_proteinas_g_hoy = sum(r.proteinas_consumidas for r in registros_hoy if r.alimento and r.cantidad is not None)
        consumo_grasas_g_hoy = sum(r.grasas_consumidas for r in registros_hoy if r.alimento and r.cantidad is not None)
        consumo_carbohidratos_g_hoy = sum(r.carbohidratos_consumidos for r in registros_hoy if r.alimento and r.cantidad is not None)
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
        # Lógica para usuarios no autenticados (página de inicio pública)
        return render(request, 'inicio_publico.html')

@login_required
def mis_objetivos(request):
    # ... (código completo de mis_objetivos como lo tenías) ...
    calorias_objetivo_diario = getattr(request.user, 'calorias_objetivo_fijadas', 2200)
    objetivo_proteinas_g = getattr(request.user, 'proteinas_objetivo_g', 150) 
    objetivo_grasas_g = getattr(request.user, 'grasas_objetivo_g', 60)
    objetivo_carbohidratos_g = getattr(request.user, 'carbohidratos_objetivo_g', 265)
    porcentaje_proteinas = round((objetivo_proteinas_g * 4 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    porcentaje_grasas = round((objetivo_grasas_g * 9 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    porcentaje_carbohidratos = round((objetivo_carbohidratos_g * 4 / calorias_objetivo_diario * 100) if calorias_objetivo_diario > 0 else 0)
    cal_desayuno = calorias_objetivo_diario * 0.20; cal_almuerzo = calorias_objetivo_diario * 0.30; cal_cena = calorias_objetivo_diario * 0.30; cal_snacks = calorias_objetivo_diario * 0.20
    minutos_ejercicio_semana = getattr(request.user, 'minutos_ejercicio_obj_semana', 150)
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
    # ... (código completo de registrar_medidas como lo tenías) ...
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
    # ... (código completo de ver_perfil como lo tenías) ...
    usuario = request.user 
    ultimas_medidas = MedidaCorporal.objects.filter(usuario=usuario).order_by('-fecha').first()
    context = {
        'usuario_perfil': usuario, 'ultimas_medidas': ultimas_medidas, 
        'active_section': 'dashboard', 'active_subsection': 'ver_perfil' 
    }
    return render(request, 'perfil.html', context)

@login_required
def diario_alimentos(request, fecha_str=None):
    # ... (código completo de diario_alimentos como en la última versión funcional) ...
    if fecha_str:
        try: fecha_seleccionada = date.fromisoformat(fecha_str)
        except ValueError: messages.error(request, _("Formato de fecha inválido.")); return redirect(reverse('diario_alimentos_hoy')) 
    else: fecha_seleccionada = timezone.localdate()
    tipo_comida_display_dict = dict(RegistroAlimentacion.TIPO_COMIDA_CHOICES)
    if request.method == 'POST':
        form_consumo_post = AnadirConsumoAlimentoForm(request.POST)
        if form_consumo_post.is_valid():
            alimento_id_form = form_consumo_post.cleaned_data.get('alimento_id')
            alimento_id_validated = form_consumo_post.cleaned_data.get('alimento_id_validated')
            alimento_id_final = alimento_id_form if alimento_id_form else alimento_id_validated
            if alimento_id_final:
                try:
                    alimento_obj = Alimento.objects.get(id=alimento_id_final)
                    cantidad = form_consumo_post.cleaned_data['cantidad']
                    fecha_consumo_form = form_consumo_post.cleaned_data['fecha']
                    tipo_comida_consumo = form_consumo_post.cleaned_data['tipo_comida']
                    RegistroAlimentacion.objects.create(
                        usuario=request.user, alimento=alimento_obj, cantidad=cantidad,
                        fecha=fecha_consumo_form, tipo_comida=tipo_comida_consumo
                    )
                    nombre_tipo_comida_display = tipo_comida_display_dict.get(tipo_comida_consumo, tipo_comida_consumo.capitalize())
                    messages.success(request, _('"{alimento}" ({cantidad}g) añadido a {tipo_comida} para el {fecha}.').format(
                        alimento=alimento_obj.nombre, cantidad=cantidad,
                        tipo_comida=nombre_tipo_comida_display, fecha=fecha_consumo_form.strftime("%d/%m/%Y")
                    ))
                    return redirect(reverse('diario_alimentos_fecha', args=[fecha_consumo_form.isoformat()]))
                except Alimento.DoesNotExist: messages.error(request, _("El alimento seleccionado ya no existe."))
            else: messages.error(request, _("No se pudo identificar el alimento."))
        else:
            for field, errors_list in form_consumo_post.errors.items():
                for error in errors_list:
                    field_label = form_consumo_post.fields[field].label if field != '__all__' and field in form_consumo_post.fields else ''
                    messages.error(request, f"{field_label}: {error}" if field_label else error)
        fecha_redirect_str = request.POST.get('fecha', fecha_seleccionada.isoformat())
        return redirect(reverse('diario_alimentos_fecha', args=[fecha_redirect_str]))
    dia_anterior = fecha_seleccionada - timedelta(days=1); dia_siguiente = fecha_seleccionada + timedelta(days=1)
    es_hoy = (fecha_seleccionada == timezone.localdate())
    registros_del_dia = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=fecha_seleccionada).order_by('fecha_creacion') 
    tipos_comida_orden = [choice[0] for choice in RegistroAlimentacion.TIPO_COMIDA_CHOICES]
    comidas_del_dia_agrupadas = {tipo_key: [] for tipo_key in tipos_comida_orden}
    for registro in registros_del_dia:
        if registro.tipo_comida in comidas_del_dia_agrupadas:
            comidas_del_dia_agrupadas[registro.tipo_comida].append(registro)
    comidas_del_dia_lista_ordenada = []
    for tipo_key in tipos_comida_orden:
        registros_para_tipo = comidas_del_dia_agrupadas[tipo_key]
        total_calorias_tipo = sum(r.calorias_consumidas for r in registros_para_tipo if r.alimento)
        comidas_del_dia_lista_ordenada.append({
            'key': tipo_key, 'nombre_display': tipo_comida_display_dict.get(tipo_key, tipo_key.capitalize()),
            'registros': registros_para_tipo, 'total_calorias': total_calorias_tipo
        })
    total_calorias_consumidas = sum(c['total_calorias'] for c in comidas_del_dia_lista_ordenada)
    total_proteinas_consumidas = sum(r.proteinas_consumidas for comida in comidas_del_dia_lista_ordenada for r in comida['registros'] if r.alimento); total_grasas_consumidas = sum(r.grasas_consumidas for comida in comidas_del_dia_lista_ordenada for r in comida['registros'] if r.alimento); total_carbohidratos_consumidos = sum(r.carbohidratos_consumidos for comida in comidas_del_dia_lista_ordenada for r in comida['registros'] if r.alimento)
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
    form_anadir_consumo_modal = AnadirConsumoAlimentoForm(initial={'fecha': fecha_seleccionada})
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
        'form_anadir_consumo_modal': form_anadir_consumo_modal,
        'active_section': 'alimentos', 'active_subsection': 'diario_alimentos'
    }
    return render(request, 'diario_alimentos.html', context)

@login_required
def actualizar_consumo_agua(request):
    # ... (código completo de actualizar_consumo_agua como lo tenías) ...
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
    # ... (código completo de buscar_alimento_db como lo tenías) ...
    query = request.GET.get('q_alimento', '')
    resultados = []
    if query:
        resultados = Alimento.objects.filter(nombre__icontains=query)
    context = {
        'resultados_busqueda': resultados, 'termino_busqueda': query,
        'active_section': 'alimentos', 'active_subsection': 'alimentos_database'
    }
    return render(request, 'alimentos_database.html', context)

@login_required
def registro_alimentacion(request): # Para crear nuevos alimentos en la BD
    # ... (código completo de registro_alimentacion como lo tenías) ...
    if request.method == 'POST':
        form = CrearAlimentoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Alimento "{}" añadido a la base de datos con éxito.').format(form.cleaned_data.get('nombre')))
                return redirect('alimentos_database')
            except Exception as e:
                print(f"Error al guardar alimento: {e}")
                messages.error(request, _('No se pudo añadir el alimento. Es posible que ya exista un alimento con ese nombre.'))
    else:
        form = CrearAlimentoForm()
    context = {
        'form': form,
        'active_section': 'alimentos',
        'active_subsection': 'registro_alimentacion'
    }
    return render(request, 'register_food.html', context)

@login_required
def sugerencias_alimentos(request):
    # ... (código completo de sugerencias_alimentos como lo tenías) ...
    q = request.GET.get('q','').strip().lower()
    data = []
    if q and len(q) >= 1:
        alimentos_sugeridos = Alimento.objects.filter(nombre__icontains=q).values('id', 'nombre')[:10]
        data = list(alimentos_sugeridos)
    return JsonResponse(data, safe=False)

@login_required
def resumen_diario(request):
    # ... (código completo de resumen_diario como lo tenías) ...
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
    # ... (código completo de lista_registros como lo tenías) ...
    registros = RegistroAlimentacion.objects.filter(usuario=request.user).order_by('-fecha', '-id')
    context = { 'registros': registros, 'active_section': 'informes', 'active_subsection': 'lista_registros' }
    return render(request, 'registros.html', context)

@login_required
def editar_registro(request, pk): # Para editar consumo de ALIMENTOS
    # ... (código completo de editar_registro (alimentos) como lo tenías) ...
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    fecha_registro_str = registro_obj.fecha.isoformat()
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['fecha'] = fecha_registro_str
        post_data['tipo_comida'] = registro_obj.tipo_comida
        form = AnadirConsumoAlimentoForm(post_data) 
        if form.is_valid():
            alimento_id_form = form.cleaned_data.get('alimento_id')
            alimento_id_validated = form.cleaned_data.get('alimento_id_validated')
            alimento_id_final = alimento_id_form if alimento_id_form else alimento_id_validated
            if alimento_id_final:
                try:
                    alimento_nuevo = Alimento.objects.get(id=alimento_id_final)
                    registro_obj.alimento = alimento_nuevo
                    registro_obj.cantidad = form.cleaned_data['cantidad']
                    registro_obj.save()
                    messages.success(request, _('Registro de alimento actualizado con éxito.'))
                    return redirect(reverse('diario_alimentos_fecha', args=[fecha_registro_str]))
                except Alimento.DoesNotExist:
                    form.add_error('alimento_nombre', _('El alimento especificado no existe.'))
            else:
                messages.error(request, _("No se pudo identificar el alimento para la actualización."))
    else:
        form = AnadirConsumoAlimentoForm(initial={
            'alimento_nombre': registro_obj.alimento.nombre,
            'cantidad': registro_obj.cantidad,
            'fecha': registro_obj.fecha,
            'tipo_comida': registro_obj.tipo_comida
        })
    context = {
        'form': form, 'registro_editando': registro_obj,
        'active_section': 'alimentos', 'fecha_diario_actual': fecha_registro_str,
        'nombre_tipo_comida_display': dict(RegistroAlimentacion.TIPO_COMIDA_CHOICES).get(registro_obj.tipo_comida, registro_obj.tipo_comida)
    }
    return render(request, 'editar_consumo_alimento.html', context)


@login_required
def eliminar_registro(request, pk): # Para eliminar consumo de ALIMENTOS
    # ... (código completo de eliminar_registro (alimentos) como lo tenías) ...
    registro_obj = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    fecha_registro_iso = registro_obj.fecha.isoformat()
    registro_obj.delete()
    messages.success(request, _('Registro de alimento eliminado correctamente.'))
    return redirect(reverse('diario_alimentos_fecha', args=[fecha_registro_iso]))


# --- SECCIÓN EJERCICIOS (VISTAS NUEVAS Y ACTUALIZADAS) ---
def actualizar_calorias_ejercicio_registradas_usuario(usuario, fecha):
    if fecha == timezone.localdate():
        total_kcal_ejercicio_del_dia = RegistroEjercicioRealizado.objects.filter(
            usuario=usuario, fecha=fecha
        ).aggregate(total_kcal=Sum('calorias_quemadas_calculadas'))['total_kcal'] or 0
        
        usuario.calorias_ejercicio_hoy_registradas = total_kcal_ejercicio_del_dia
        usuario.save(update_fields=['calorias_ejercicio_hoy_registradas'])

@login_required
def ver_ejercicios(request, fecha_str=None):
    # ... (código completo de ver_ejercicios que te di en el mensaje anterior) ...
    if fecha_str:
        try: fecha_seleccionada = date.fromisoformat(fecha_str)
        except ValueError: messages.error(request, _("Formato de fecha inválido.")); return redirect(reverse('ver_ejercicios'))
    else: fecha_seleccionada = timezone.localdate()
    usuario = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        form_valid = False
        if action == 'add_cardio':
            form_cardio = RegistrarEjercicioCardioForm(request.POST)
            if form_cardio.is_valid():
                ejercicio_id = form_cardio.cleaned_data.get('ejercicio_id_validated') or form_cardio.cleaned_data.get('ejercicio_id')
                try:
                    ejercicio_obj = Ejercicio.objects.get(id=ejercicio_id, tipo='cardio')
                    RegistroEjercicioRealizado.objects.create(
                        usuario=usuario, ejercicio=ejercicio_obj, fecha=form_cardio.cleaned_data['fecha'],
                        duracion_minutos=form_cardio.cleaned_data['duracion_minutos']
                    )
                    messages.success(request, _("Ejercicio cardiovascular '{nombre}' añadido.").format(nombre=ejercicio_obj.nombre))
                    form_valid = True
                except Ejercicio.DoesNotExist: messages.error(request, _("Ejercicio cardiovascular no encontrado."))
            else: 
                for field, errors_list in form_cardio.errors.items():
                    for error in errors_list: messages.error(request, f"{form_cardio.fields[field].label if field != '__all__' and field in form_cardio.fields else ''}: {error}")
        elif action == 'add_fuerza':
            form_fuerza = RegistrarEjercicioFuerzaForm(request.POST)
            if form_fuerza.is_valid():
                ejercicio_id = form_fuerza.cleaned_data.get('ejercicio_id_validated') or form_fuerza.cleaned_data.get('ejercicio_id')
                try:
                    ejercicio_obj = Ejercicio.objects.get(id=ejercicio_id, tipo='fuerza')
                    RegistroEjercicioRealizado.objects.create(
                        usuario=usuario, ejercicio=ejercicio_obj, fecha=form_fuerza.cleaned_data['fecha'],
                        series=form_fuerza.cleaned_data.get('series'),
                        repeticiones_por_serie=form_fuerza.cleaned_data.get('repeticiones_por_serie'),
                        peso_utilizado_kg=form_fuerza.cleaned_data.get('peso_utilizado_kg')
                    )
                    messages.success(request, _("Ejercicio de fuerza '{nombre}' añadido.").format(nombre=ejercicio_obj.nombre))
                    form_valid = True
                except Ejercicio.DoesNotExist: messages.error(request, _("Ejercicio de fuerza no encontrado."))
            else:
                for field, errors_list in form_fuerza.errors.items():
                    for error in errors_list: messages.error(request, f"{form_fuerza.fields[field].label if field != '__all__' and field in form_fuerza.fields else ''}: {error}")
        elif action == 'save_nota_ejercicio':
            nota_obj, created = NotaDiariaEjercicio.objects.get_or_create(usuario=usuario, fecha=fecha_seleccionada)
            form_nota = NotaDiariaEjercicioForm(request.POST, instance=nota_obj)
            if form_nota.is_valid():
                form_nota.save(); messages.success(request, _("Nota del día guardada.")); form_valid = True
            else:
                for field, errors_list in form_nota.errors.items():
                    for error in errors_list: messages.error(request, f"{form_nota.fields[field].label if field != '__all__' and field in form_nota.fields else ''}: {error}")
        if form_valid:
            actualizar_calorias_ejercicio_registradas_usuario(usuario, fecha_seleccionada)
        return redirect(reverse('ver_ejercicios_fecha', args=[fecha_seleccionada.isoformat()]))
    dia_anterior = fecha_seleccionada - timedelta(days=1); dia_siguiente = fecha_seleccionada + timedelta(days=1)
    es_hoy = (fecha_seleccionada == timezone.localdate())
    registros_ejercicio_todos = RegistroEjercicioRealizado.objects.filter(usuario=usuario, fecha=fecha_seleccionada).select_related('ejercicio')
    registros_ejercicio_cardio = [r for r in registros_ejercicio_todos if r.ejercicio.tipo == 'cardio']
    registros_ejercicio_fuerza = [r for r in registros_ejercicio_todos if r.ejercicio.tipo == 'fuerza']
    total_minutos_cardio_dia = sum(r.duracion_minutos for r in registros_ejercicio_cardio if r.duracion_minutos)
    total_calorias_ejercicio_dia = sum(r.calorias_quemadas_calculadas for r in registros_ejercicio_todos)
    calorias_ejercicio_semana_obj_usr = getattr(usuario, 'calorias_ejercicio_semana_obj', 700)
    entrenamientos_semana_obj_usr = getattr(usuario, 'entrenamientos_semana_obj', 3)
    if entrenamientos_semana_obj_usr > 0 and calorias_ejercicio_semana_obj_usr > 0 :
        objetivo_calorias_ejercicio_dia = round(calorias_ejercicio_semana_obj_usr / entrenamientos_semana_obj_usr)
    elif calorias_ejercicio_semana_obj_usr > 0:
         objetivo_calorias_ejercicio_dia = round(calorias_ejercicio_semana_obj_usr / 7)
    else: objetivo_calorias_ejercicio_dia = 150 
    objetivo_minutos_diarios_salud = 30
    form_add_cardio = RegistrarEjercicioCardioForm(initial={'fecha': fecha_seleccionada})
    form_add_fuerza = RegistrarEjercicioFuerzaForm(initial={'fecha': fecha_seleccionada})
    nota_dia_obj, created = NotaDiariaEjercicio.objects.get_or_create(usuario=usuario, fecha=fecha_seleccionada)
    form_nota_ejercicio = NotaDiariaEjercicioForm(instance=nota_dia_obj)
    context = {
        'fecha_seleccionada_str': fecha_seleccionada.isoformat(), 'fecha_seleccionada_display': fecha_seleccionada,
        'dia_anterior_str': dia_anterior.isoformat(), 'dia_siguiente_str': dia_siguiente.isoformat(), 'es_hoy': es_hoy,
        'registros_cardio': registros_ejercicio_cardio, 'registros_fuerza': registros_ejercicio_fuerza,
        'total_minutos_cardio_dia': total_minutos_cardio_dia, 'total_calorias_ejercicio_dia': total_calorias_ejercicio_dia,
        'objetivo_calorias_ejercicio_dia': objetivo_calorias_ejercicio_dia,
        'objetivo_minutos_diarios_salud': objetivo_minutos_diarios_salud,
        'form_add_cardio': form_add_cardio, 'form_add_fuerza': form_add_fuerza,
        'form_nota_ejercicio': form_nota_ejercicio,
        'nota_existente_texto': nota_dia_obj.texto_nota if not created or nota_dia_obj.texto_nota else "",
        'active_section': 'ejercicio', 'active_subsection': 'ver_ejercicios'
    }
    return render(request, 'registro_ejercicio_diario.html', context)

@login_required
def editar_registro_ejercicio(request, pk):
    # ... (código completo de editar_registro_ejercicio que te di en el mensaje anterior) ...
    registro_ej = get_object_or_404(RegistroEjercicioRealizado, pk=pk, usuario=request.user)
    fecha_original_str = registro_ej.fecha.isoformat()
    FormularioAUsar = RegistrarEjercicioCardioForm if registro_ej.ejercicio.tipo == 'cardio' else RegistrarEjercicioFuerzaForm
    if request.method == 'POST':
        post_data = request.POST.copy(); post_data['fecha'] = fecha_original_str 
        form = FormularioAUsar(post_data)
        if form.is_valid():
            ejercicio_id_form = form.cleaned_data.get('ejercicio_id'); ejercicio_id_validated = form.cleaned_data.get('ejercicio_id_validated')
            ejercicio_id_final = ejercicio_id_form if ejercicio_id_form else ejercicio_id_validated
            if not ejercicio_id_final and form.cleaned_data.get('ejercicio_nombre') == registro_ej.ejercicio.nombre:
                ejercicio_id_final = registro_ej.ejercicio.id
            if ejercicio_id_final:
                try:
                    nuevo_ejercicio_obj = Ejercicio.objects.get(id=ejercicio_id_final, tipo=registro_ej.ejercicio.tipo)
                    registro_ej.ejercicio = nuevo_ejercicio_obj
                    if registro_ej.ejercicio.tipo == 'cardio':
                        registro_ej.duracion_minutos = form.cleaned_data.get('duracion_minutos')
                        registro_ej.series, registro_ej.repeticiones_por_serie, registro_ej.peso_utilizado_kg = None, None, None
                    else: 
                        registro_ej.series = form.cleaned_data.get('series'); registro_ej.repeticiones_por_serie = form.cleaned_data.get('repeticiones_por_serie')
                        registro_ej.peso_utilizado_kg = form.cleaned_data.get('peso_utilizado_kg'); registro_ej.duracion_minutos = None
                    registro_ej.save() 
                    actualizar_calorias_ejercicio_registradas_usuario(request.user, registro_ej.fecha)
                    messages.success(request, _("Registro de ejercicio actualizado."))
                    return redirect(reverse('ver_ejercicios_fecha', args=[fecha_original_str]))
                except Ejercicio.DoesNotExist: form.add_error('ejercicio_nombre', _("El ejercicio seleccionado no es válido o su tipo no coincide."))
            else: form.add_error('ejercicio_nombre', _("Por favor, selecciona un ejercicio válido de la lista."))
    else: 
        initial_data = {
            'ejercicio_nombre': registro_ej.ejercicio.nombre, 'ejercicio_id': registro_ej.ejercicio.id, 'fecha': registro_ej.fecha,
        }
        if registro_ej.ejercicio.tipo == 'cardio': initial_data['duracion_minutos'] = registro_ej.duracion_minutos
        else:
            initial_data['series'] = registro_ej.series; initial_data['repeticiones_por_serie'] = registro_ej.repeticiones_por_serie
            initial_data['peso_utilizado_kg'] = registro_ej.peso_utilizado_kg
        form = FormularioAUsar(initial=initial_data)
    context = {
        'form': form, 'registro_ejercicio': registro_ej, 'tipo_ejercicio': registro_ej.ejercicio.tipo,
        'active_section': 'ejercicio', 'fecha_seleccionada_str': fecha_original_str,
    }
    return render(request, 'editar_registro_ejercicio.html', context)

@login_required
def eliminar_registro_ejercicio(request, pk):
    # ... (código completo de eliminar_registro_ejercicio que te di en el mensaje anterior) ...
    registro_ej = get_object_or_404(RegistroEjercicioRealizado, pk=pk, usuario=request.user)
    fecha_registro_str = registro_ej.fecha.isoformat(); fecha_registro_obj = registro_ej.fecha
    registro_ej.delete()
    actualizar_calorias_ejercicio_registradas_usuario(request.user, fecha_registro_obj)
    messages.success(request, _("Registro de ejercicio eliminado."))
    return redirect(reverse('ver_ejercicios_fecha', args=[fecha_registro_str]))

@login_required
def database_ejercicios(request):
    # ... (código completo de database_ejercicios como lo tenías) ...
    grupos_disponibles_choices = Ejercicio.GRUPO_MUSCULAR_CHOICES
    grupos_para_plantilla = []
    for clave, nombre_legible in grupos_disponibles_choices:
        if clave:
            grupos_para_plantilla.append({ 'clave': clave, 'nombre_display': nombre_legible, })
    context = {
        'grupos_ejercicios': grupos_para_plantilla,
        'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'
    }
    return render(request, 'database_ejercicios.html', context)

@login_required
def vista_pecho(request):
    # ... (código completo de vista_pecho como lo tenías) ...
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='pecho').order_by('nombre')
    context = {
        'grupo_nombre_display': _('Pecho'), 'ejercicios_list': ejercicios_grupo,
        'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'
    }
    return render(request, 'grupo_base.html', context)

# ... (Asegúrate de tener TODAS las vistas de grupo: vista_espalda, vista_piernas, etc., como estaban)

@login_required
def vista_espalda(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='espalda').order_by('nombre')
    context = { 'grupo_nombre_display': _('Espalda'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)
@login_required
def vista_piernas(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='piernas').order_by('nombre')
    context = { 'grupo_nombre_display': _('Piernas'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)
@login_required
def vista_hombros(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='hombros').order_by('nombre')
    context = { 'grupo_nombre_display': _('Hombros'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)
@login_required
def vista_brazos(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='brazos').order_by('nombre')
    context = { 'grupo_nombre_display': _('Brazos'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)
@login_required
def vista_abdominales(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='abdominales').order_by('nombre')
    context = { 'grupo_nombre_display': _('Abdominales'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)
@login_required
def vista_cardio_general(request):
    ejercicios_grupo = Ejercicio.objects.filter(grupo_muscular='cardio_general').order_by('nombre')
    context = { 'grupo_nombre_display': _('Cardiovascular'), 'ejercicios_list': ejercicios_grupo, 'active_section': 'ejercicio', 'active_subsection': 'database_ejercicios'}
    return render(request, 'grupo_base.html', context)

@login_required
def sugerencias_ejercicios(request):
    # ... (código completo de sugerencias_ejercicios como lo tenías) ...
    q = request.GET.get('q','').strip().lower()
    tipo_ejercicio_query = request.GET.get('tipo_ejercicio', None)
    data = []
    if q and len(q) >= 1:
        query_filter = Q(nombre__icontains=q)
        if tipo_ejercicio_query == 'cardio': query_filter &= Q(tipo='cardio')
        elif tipo_ejercicio_query == 'fuerza': query_filter &= Q(tipo='fuerza')
        ejercicios_sugeridos = Ejercicio.objects.filter(query_filter).values('id', 'nombre', 'tipo')[:10]
        data = list(ejercicios_sugeridos)
    return JsonResponse(data, safe=False)

# --- VISTAS Y CONFIGURACIÓN DEL ASISTENTE DE REGISTRO ---
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
    
    def get_template_names(self):
        return [REGISTRATION_TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = {k: v for form in form_list for k, v in form.cleaned_data.items()}
        try:
            user = Usuario.objects.create_user(
                username=form_data.get('username'), email=form_data.get('email'), password=form_data.get('password')
            )
            user.first_name = form_data.get('first_name', ''); user.objetivo = form_data.get('objetivo')
            user.actividad_fisica = form_data.get('actividad_fisica', ''); user.edad = form_data.get('edad')
            user.peso = form_data.get('peso'); user.altura = form_data.get('altura'); user.sexo = form_data.get('sexo')
            user.save() 
            user.calorias_objetivo_fijadas = calcular_calorias_objetivo_ingesta(user) # Usar la función importada
            user.save(update_fields=['calorias_objetivo_fijadas'])
            auth_login(self.request, user)
            messages.success(self.request, _('¡Bienvenido a NutriControl! Tu cuenta ha sido creada y configurada exitosamente.'))
            return redirect('dashboard')
        except Exception as e:
            print(f"Error en RegistrationWizard done: {e}")
            messages.error(self.request, _("Hubo un error inesperado al crear tu cuenta. Por favor, intenta de nuevo."))
            return redirect('registration_welcome')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step_name = self.steps.current
        progress_denominator = len(self.form_list) if len(self.form_list) > 0 else 1
        context['progress_percentage'] = round(((self.steps.step1 -1) / progress_denominator) * 100)
        step_info = {
            "nombre": {"title": _("Para empezar, ¿cómo te llamas?"), "description": _("Nos ayudará a personalizar tu experiencia en NutriControl.")},
            "objetivos": {"title_base": _("Ahora vamos con tus objetivos"), "description": _("Selecciona tu objetivo principal. Esto nos ayudará a enfocarnos.")},
            "detalles_fisicos": {"title": _("Algunos detalles sobre ti"), "description": _("Esta información nos ayuda a calcular tus necesidades y personalizar tu plan.")},
            "credenciales": {"title": _("Crea tus credenciales de acceso"), "description": _("Elige un nombre de usuario y una contraseña segura.")}
        }
        default_title = _("Registro - Paso {} de {}").format(self.steps.step1, len(self.form_list))
        step_title_to_display = step_info.get(current_step_name, {}).get('title', default_title)
        if current_step_name == 'objetivos':
            cleaned_data_nombre = self.get_cleaned_data_for_step('nombre')
            user_name_from_previous_step = cleaned_data_nombre.get('first_name') if cleaned_data_nombre else None
            objetivos_base_title = step_info.get("objetivos", {}).get("title_base", _("Ahora vamos con tus objetivos"))
            if user_name_from_previous_step:
                step_title_to_display = f"¡Gracias, {user_name_from_previous_step}! {objetivos_base_title.lower()}"
            else: step_title_to_display = f"¡Gracias! {objetivos_base_title.lower()}"
        context['step_title_from_view'] = step_title_to_display
        context['step_description_from_view'] = step_info.get(current_step_name, {}).get('description', "")
        return context