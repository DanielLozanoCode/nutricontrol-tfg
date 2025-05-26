import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutricontrol.settings')
django.setup()

from base.models import Alimento

alimentos = [
    ("Pollo", 165, 31, 3.6, 0),
    ("Arroz blanco", 130, 2.7, 0.3, 28),
    ("Avena", 389, 16.9, 6.9, 66),
    ("Manzana", 52, 0.3, 0.2, 14),
    ("Huevo", 155, 13, 11, 1.1),
    ("Brócoli", 34, 2.8, 0.4, 7),
    ("Salmón", 208, 20, 13, 0),
    ("Pan integral", 247, 13, 4.2, 41),
    ("Aceite de oliva", 884, 0, 100, 0),
    ("Leche desnatada", 35, 3.4, 0.1, 5),
]

for nombre, calorias, proteinas, grasas, carbohidratos in alimentos:
    Alimento.objects.get_or_create(
        nombre=nombre,
        calorias=calorias,
        proteinas=proteinas,
        grasas=grasas,
        carbohidratos=carbohidratos
    )

print("✅ Alimentos cargados correctamente.")
