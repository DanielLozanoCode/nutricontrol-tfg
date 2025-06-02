# base/management/commands/load_exercises.py

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from base.models import Ejercicio # Importa tu modelo Ejercicio
from django.utils.translation import gettext_lazy as _

class Command(BaseCommand):
    help = 'Carga ejercicios desde archivos JSON a la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Limpiando la tabla de Ejercicios existente...'))
        Ejercicio.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Tabla de Ejercicios limpiada.'))

        json_folder_path = os.path.join(settings.BASE_DIR, 'base', 'static', 'base', 'json')
        json_files = [
            'abdominales.json', 'brazos.json', 'cardio.json',
            'espalda.json', 'hombros.json', 'pecho.json', 'piernas.json'
        ]

        grupo_muscular_map = {
            "Abdominales": "abdominales", "Brazos": "brazos",
            "Cardiovascular": "cardio_general", "Espalda": "espalda",
            "Hombros": "hombros", "Pecho": "pecho", "Piernas": "piernas",
        }

        ejercicios_cargados = 0
        ejercicios_omitidos = 0

        for json_file_name in json_files:
            file_path = os.path.join(json_folder_path, json_file_name)
            self.stdout.write(f"Procesando archivo: {json_file_name}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_grupo_nombre = data.get("grupo")
                    modelo_grupo_muscular_key = grupo_muscular_map.get(json_grupo_nombre)

                    # AJUSTE AQUÍ: Si no hay mapeo y NO es cardio, lo dejamos como None
                    # ya que 'otro' no es una opción válida.
                    # El campo grupo_muscular en el modelo permite null=True.
                    if not modelo_grupo_muscular_key and json_grupo_nombre:
                        tipo_ejercicio_temporal = data.get("ejercicios", [{}])[0].get("tipo", "").lower()
                        if tipo_ejercicio_temporal != "cardio":
                             self.stdout.write(self.style.WARNING(f"  ADVERTENCIA: El grupo de fuerza '{json_grupo_nombre}' del JSON no tiene mapeo en 'grupo_muscular_map'. Se asignará grupo_muscular=None."))
                             modelo_grupo_muscular_key = None # Asignar None
                        # Si es cardio, se manejará abajo para asegurar 'cardio_general'

                    for ejercicio_data in data.get("ejercicios", []):
                        nombre = ejercicio_data.get("nombre")
                        tipo_ejercicio_json = ejercicio_data.get("tipo")
                        descripcion = ejercicio_data.get("descripcion")
                        video_url = ejercicio_data.get("video_url")
                        calorias_base = ejercicio_data.get("calorias_quemadas_base")

                        if not nombre or not tipo_ejercicio_json or calorias_base is None:
                            self.stdout.write(self.style.ERROR(f"  ERROR: Datos incompletos para el ejercicio '{nombre}' en {json_file_name}. Se omite."))
                            ejercicios_omitidos += 1
                            continue
                        
                        grupo_para_modelo = modelo_grupo_muscular_key
                        if tipo_ejercicio_json == "cardio":
                            grupo_para_modelo = "cardio_general"

                        # Si después de todo, grupo_para_modelo es None y es de fuerza,
                        # podrías decidir omitirlo o loggearlo más específicamente.
                        # Por ahora, se guardará con grupo_muscular=None si así quedó.

                        try:
                            ejercicio_obj, created = Ejercicio.objects.update_or_create(
                                nombre=nombre,
                                defaults={
                                    'tipo': tipo_ejercicio_json,
                                    'grupo_muscular': grupo_para_modelo,
                                    'descripcion': descripcion,
                                    'video_url': video_url,
                                    'calorias_quemadas_base': int(calorias_base)
                                }
                            )
                            if created:
                                ejercicios_cargados += 1
                            # else:
                                # self.stdout.write(self.style.NOTICE(f"  Ejercicio '{nombre}' actualizado."))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"  ERROR al guardar el ejercicio '{nombre}': {e}"))
                            ejercicios_omitidos += 1
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f"Archivo no encontrado: {file_path}"))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"Error al decodificar JSON en: {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error inesperado procesando {json_file_name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Carga de ejercicios completada. {ejercicios_cargados} nuevos ejercicios cargados, {ejercicios_omitidos} omitidos.'))