import os, csv, json

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH    = os.path.join(BASE_DIR, 'base', 'static', 'base', 'foods100.csv')
OUTPUT_JSON = os.path.join(BASE_DIR, 'base', 'static', 'base', 'foods.json')
TARGET      = 300   # o 100, los que tengas en tu CSV

def main():
    if not os.path.exists(CSV_PATH):
        print("❌ No encuentro foods100.csv en", CSV_PATH); return

    names, seen = [], set()
    with open(CSV_PATH, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre = row['Nombre'].strip()
            if nombre and nombre.lower() not in seen:
                names.append(nombre)
                seen.add(nombre.lower())
            if len(names) >= TARGET:
                break

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as out:
        json.dump(names, out, ensure_ascii=False, indent=2)

    print(f"✅ Generados {len(names)} nombres en {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
