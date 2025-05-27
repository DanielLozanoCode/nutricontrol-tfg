import os
import json
import requests

from datetime import date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET

from .forms import RegistroForm, RegistroAlimentacionForm
from .models import Alimento, RegistroAlimentacion


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada con éxito! Ahora puedes iniciar sesión.')
            return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'register.html', {'form': form})


def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html') 
    else:
        return render(request, 'inicio_publico.html')


@login_required
def registro_alimentacion(request):
    if request.method == 'POST':
        form = RegistroAlimentacionForm(request.POST)
        if form.is_valid():
            nombre   = form.cleaned_data['alimento_nombre']
            cantidad = form.cleaned_data['cantidad']
            try:
                alimento = Alimento.objects.get(nombre__iexact=nombre)
            except Alimento.DoesNotExist:
                messages.error(request, 'Ese alimento no existe aún en la base de datos.')
                return redirect('registro_alimentacion')

            RegistroAlimentacion.objects.create(
                usuario=request.user,
                alimento=alimento,
                cantidad=cantidad
            )
            messages.success(request, 'Registro de alimentación guardado con éxito.')
            return redirect('dashboard')
    else:
        form = RegistroAlimentacionForm()
    return render(request, 'register_food.html', {'form': form})


@login_required
def sugerencias_alimentos(request):
    q    = request.GET.get('q','').strip().lower()
    path = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', 'foods.json')
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    resultados = [item for item in data if q in item['nombre'].lower()][:10]
    return JsonResponse(resultados, safe=False)


@login_required
def resumen_diario(request):
    hoy       = date.today()
    registros = RegistroAlimentacion.objects.filter(usuario=request.user, fecha=hoy)

    total_calorias      = total_proteinas = total_grasas = total_carbohidratos = 0
    for r in registros:
        factor = r.cantidad / 100
        total_calorias      += r.alimento.calorias      * factor
        total_proteinas     += r.alimento.proteinas     * factor
        total_grasas        += r.alimento.grasas        * factor
        total_carbohidratos += r.alimento.carbohidratos * factor

    return render(request, 'resumen_diario.html', {
        'registros':           registros,
        'fecha':               hoy,
        'total_calorias':      total_calorias,
        'total_proteinas':     total_proteinas,
        'total_grasas':        total_grasas,
        'total_carbohidratos': total_carbohidratos,
    })


@login_required
def lista_registros(request):
    registros = RegistroAlimentacion.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'registros.html', {'registros': registros})


@login_required
def eliminar_registro(request, pk):
    registro = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    registro.delete()
    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('lista_registros')


@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(RegistroAlimentacion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = RegistroAlimentacionForm(request.POST)
        if form.is_valid():
            nombre   = form.cleaned_data['alimento_nombre']
            cantidad = form.cleaned_data['cantidad']
            try:
                alimento           = Alimento.objects.get(nombre__iexact=nombre)
                registro.alimento  = alimento
                registro.cantidad  = cantidad
                registro.save()
                messages.success(request, 'Registro actualizado correctamente.')
                return redirect('lista_registros')
            except Alimento.DoesNotExist:
                messages.error(request, 'Ese alimento no está en la base de datos.')
    else:
        form = RegistroAlimentacionForm(initial={
            'alimento_nombre': registro.alimento.nombre,
            'cantidad':        registro.cantidad,
        })
    return render(request, 'editar_registro.html', {'form': form})


@login_required
def ver_ejercicios(request):
    path = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', 'ejercicios_por_grupo_completo.json')
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            grupos = data.get('muscle_groups', [])
    except FileNotFoundError:
        grupos = []
        messages.error(request, "No se pudo cargar el archivo de ejercicios.")
    return render(request, 'ejercicios.html', {'grupos': grupos})

def cargar_ejercicios_por_grupo(nombre_archivo):
    ruta = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', nombre_archivo)
    try:
        with open(ruta, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"grupo": "", "ejercicios": []}

@login_required
def vista_pecho(request):
    datos = cargar_ejercicios_por_grupo('pecho.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

@login_required
def vista_espalda(request):
    datos = cargar_ejercicios_por_grupo('espalda.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

@login_required
def vista_piernas(request):
    datos = cargar_ejercicios_por_grupo('piernas.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

@login_required
def vista_hombros(request):
    datos = cargar_ejercicios_por_grupo('hombros.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

@login_required
def vista_brazos(request):
    datos = cargar_ejercicios_por_grupo('brazos.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

@login_required
def vista_abdominales(request):
    datos = cargar_ejercicios_por_grupo('abdominales.json')
    return render(request, 'grupo_base.html', {
        'grupo': datos['grupo'],
        'ejercicios': datos['ejercicios']
    })

def inicio_publico(request):
    return render(request, 'inicio_publico.html')
