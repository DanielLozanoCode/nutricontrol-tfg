# base/calculations.py

from django.utils.translation import gettext_lazy as _

# Factores de actividad física (ejemplos, ajustar según necesidad)
FACTORES_ACTIVIDAD = {
    'sedentario': 1.2,        # Poco o ningún ejercicio
    'ligero': 1.375,          # Ejercicio ligero 1-3 días/semana
    'moderado': 1.55,         # Ejercicio moderado 3-5 días/semana
    'activo': 1.725,          # Ejercicio intenso 6-7 días/semana
    'muy_activo': 1.9         # Ejercicio muy intenso y/o trabajo físico
}

def _get_activity_factor(actividad_fisica_str):
    """Intenta mapear el string de actividad física a una clave de FACTORES_ACTIVIDAD."""
    if not actividad_fisica_str:
        return FACTORES_ACTIVIDAD['sedentario']
    
    normalized_str = actividad_fisica_str.lower()
    
    if "muy activo" in normalized_str or "muy_activo" in normalized_str:
        return FACTORES_ACTIVIDAD['muy_activo']
    if "activo" in normalized_str or "intenso" in normalized_str or "6-7" in normalized_str: # Ej: "Activo", "Ejercicio intenso 6-7 dias"
        return FACTORES_ACTIVIDAD['activo']
    if "moderado" in normalized_str or "3-5" in normalized_str: # Ej: "Moderado", "3-5 dias gimnasio"
        return FACTORES_ACTIVIDAD['moderado']
    if "ligero" in normalized_str or "1-3" in normalized_str or "1-2" in normalized_str: # Ej: "Ligero", "Ejercicio ligero 1-2/sem"
        return FACTORES_ACTIVIDAD['ligero']
    
    return FACTORES_ACTIVIDAD['sedentario'] # Default si no hay coincidencia clara

def calcular_tmb_mifflin_st_jeor(peso_kg, altura_cm, edad_anos, sexo_char):
    """
    Calcula la Tasa Metabólica Basal (TMB) usando la ecuación de Mifflin-St Jeor.
    sexo_char: 'H' para Hombre, 'M' para Mujer.
    """
    if not all([peso_kg, altura_cm, edad_anos, sexo_char]):
        return None # No se puede calcular si faltan datos

    if sexo_char == 'H': # Hombre
        tmb = (10 * float(peso_kg)) + (6.25 * float(altura_cm)) - (5 * int(edad_anos)) + 5
    elif sexo_char == 'M': # Mujer
        tmb = (10 * float(peso_kg)) + (6.25 * float(altura_cm)) - (5 * int(edad_anos)) - 161
    else:
        return None # Sexo no reconocido
    return tmb

def calcular_calorias_objetivo_ingesta(usuario):
    """
    Calcula las calorías de ingesta objetivo para un usuario.
    Actualiza el campo 'calorias_objetivo_fijadas' del usuario si se calcula un nuevo valor.
    """
    if not all([usuario.peso, usuario.altura, usuario.edad, usuario.sexo, usuario.actividad_fisica, usuario.objetivo]):
        # Si faltan datos críticos, no se puede calcular, se retorna el valor que ya tiene (o default si es nuevo)
        return usuario.calorias_objetivo_fijadas if usuario.calorias_objetivo_fijadas else 2200

    tmb = calcular_tmb_mifflin_st_jeor(usuario.peso, usuario.altura, usuario.edad, usuario.sexo)
    if tmb is None:
        return usuario.calorias_objetivo_fijadas # No se pudo calcular TMB

    factor_actividad = _get_activity_factor(usuario.actividad_fisica)
    calorias_mantenimiento = tmb * factor_actividad

    calorias_objetivo_final = calorias_mantenimiento

    # Ajuste según el objetivo principal del usuario
    if usuario.objetivo == 'def':    # Definición
        calorias_objetivo_final -= 500  # Déficit calórico sugerido
    elif usuario.objetivo == 'vol':  # Volumen
        calorias_objetivo_final += 300  # Superávit calórico sugerido
    elif usuario.objetivo == 'res':  # Resistencia
        # Para resistencia, podría ser mantenimiento o un ligero superávit,
        # dependiendo de la intensidad y duración. Por ahora, mantenimiento o ligero ajuste.
        calorias_objetivo_final += 100 
    # Si es 'man' (Mantenimiento), ya está en calorias_mantenimiento.

    calorias_calculadas = round(calorias_objetivo_final)
    
    # Opcional: Actualizar directamente el campo del usuario si se desea que esta función tenga ese efecto secundario.
    # Si se hace, considerar cuándo llamar a usuario.save().
    # Por ahora, la función solo calcula y devuelve el valor. La vista que la llame se encargará de guardar.
    # usuario.calorias_objetivo_fijadas = calorias_calculadas
    # usuario.save(update_fields=['calorias_objetivo_fijadas'])
    
    return calorias_calculadas