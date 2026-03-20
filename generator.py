import json
from jinja2 import Template

# Wczytaj szablony i dane
with open("template.json", "r", encoding="utf-8") as f:
    template_str = f.read()

with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

template = Template(template_str)
results = []

# Iteracja i produkcja
for entry in dataset:
    # Renderujemy string szablonu z danymi
    rendered_str = template.render(entry)
    # Parsujemy go z powrotem na obiekt, żeby mieć ładny JSON
    results.append(json.loads(rendered_str))

# Zapisujemy finalną tablicę
with open("final_batch.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Wygenerowano final_batch.json!")
