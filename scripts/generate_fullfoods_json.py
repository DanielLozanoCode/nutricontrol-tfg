import os, csv, json

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH    = os.path.join(BASE_DIR, 'base', 'static', 'base', 'foods100.csv')
OUTPUT_JSON = os.path.join(BASE_DIR, 'base', 'static', 'base', 'foods.json')  # lo mismo
TARGET      = 100

def main():
    items = []
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= TARGET: break
            items.append({
                'nombre':        row['Nombre'].strip(),
                'calorias':      float(row['Calorias']),
                'proteinas':     float(row['Proteinas']),
                'carbohidratos': float(row['Carbohidratos']),
                'grasas':        float(row['Grasas']),
            })
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as out:
        json.dump(items, out, ensure_ascii=False, indent=2)
    print(f"✅ Generado {len(items)} objetos con macros en {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
