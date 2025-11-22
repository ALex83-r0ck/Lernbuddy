# utils/json_to_jsonl.py
import json
import ollama

def generate_simple_answers(detailed: str):
    prompt = f"""
Erstelle aus dieser Antwort:

{detailed}

1) Eine extrem kurze, vereinfachte Ein-Satz-Antwort.
2) Drei bis fünf Bullet-Points, die die Antwort besonders verständlich zusammenfassen.

Ausgabe im JSON-Format:
{{
  "simple": "...",
  "ultra_simple": ["...", "..."]
}}
"""

    try:
        r = ollama.generate(model="gemma2:2b", prompt=prompt)
        return json.loads(r["response"])
    except:
        # Fallback
        return {
            "simple": detailed[:120] + "..." if len(detailed) > 120 else detailed,
            "ultra_simple": [detailed]
        }


with open("data/fragen.json", encoding="utf-8") as f:
    data = json.load(f)

with open("data/cards.jsonl", "w", encoding="utf-8") as f:
    for card in data["cards"]:

        card.setdefault("answer", {})
        card["answer"].setdefault("detailed", "")
        
        # Wenn simple/ultra_simple fehlen → generieren
        gen = generate_simple_answers(card["answer"]["detailed"])
        card["answer"]["simple"] = gen["simple"]
        card["answer"]["ultra_simple"] = gen["ultra_simple"]

        # weitere Felder setzen
        card["difficulty"] = None
        card["correct_streak"] = 0
        card["last_reviewed"] = None

        f.write(json.dumps(card, ensure_ascii=False) + "\n")
