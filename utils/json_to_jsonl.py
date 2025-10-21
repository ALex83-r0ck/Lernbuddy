import json 

with open('data/fragen.json') as f:
    data = json.load(f)

with open('data/cards.jsonl', 'w') as f:
    for card in data["cards"]:
        card["difficulty"] = None
        card["last_review"] = None
        card["correct_streak"] = 0
        f.write(json.dumps(card, ensure_ascii=False) + '\n')