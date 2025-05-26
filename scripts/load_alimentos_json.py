#!/usr/bin/env python
import os, sys, json

# 1) Inserta la carpeta raíz (donde está manage.py) en el path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 2) Apunta a tu settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutricontrol.settings')

import django
django.setup()

from base.models import Alimento

# 3) Ruta a tu JSON con macros
JSON_PATH = os.path.join(BASE_DIR, 'base', 'static', 'base', 'foods.json')

def main():
    if not os.path.exists(JSON_PATH):
        print(f"❌ No encuentro {JSON_PATH}")
        return

    with open(JSON_PATH, encoding='utf-8') as f:
        items = json.load(f)

    # 4) Borra registros previos (opcional pero recomendable)
    Alimento.objects.all().delete()

    # 5) Crea en BD
    for entry in items:
        Alimento.objects.create(
            nombre        = entry['nombre'],
            calorias      = entry['calorias'],
            proteinas     = entry['proteinas'],
            carbohidratos = entry['carbohidratos'],
            grasas        = entry['grasas'],
        )
    print(f"✅ Importados {len(items)} alimentos en la BD.")

if __name__ == "__main__":
    main()
