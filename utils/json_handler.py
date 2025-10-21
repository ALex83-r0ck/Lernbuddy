# utils/json_handler.py
import json
import os
from datetime import datetime

DATA_FILE = "data/cards.jsonl"

class CardStorage:
    def __init__(self):
        self.file_path = DATA_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass  # Leere JSONL-Datei

    def load_cards(self):
        cards = []
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            card = json.loads(line)
                            # Sicherstellen, dass Lernfelder existieren
                            for field in ["difficulty", "correct_streak", "last_reviewed"]:
                                if field not in card:
                                    card[field] = None if field != "correct_streak" else 0
                            cards.append(card)
                        except json.JSONDecodeError:
                            continue
        return cards

    def save_cards(self, cards):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                for card in cards:
                    f.write(json.dumps(card, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

    def card_number_exists(self, karten_nummer):
        return any(c.get("karten_nummer") == karten_nummer for c in self.load_cards())

    def add_card(self, card_data):
        if self.card_number_exists(card_data.get("karten_nummer")):
            return False

        cards = self.load_cards()
        card_data["id"] = max([c.get("id", 0) for c in cards], default=0) + 1
        card_data["difficulty"] = None
        card_data["correct_streak"] = 0
        card_data["last_reviewed"] = None
        cards.append(card_data)
        return self.save_cards(cards)

    def get_card_by_number(self, karten_nummer):
        return next((c for c in self.load_cards() if c.get("karten_nummer") == karten_nummer), None)

    def delete_card(self, karten_nummer):
        cards = [c for c in self.load_cards() if c.get("karten_nummer") != karten_nummer]
        return self.save_cards(cards)

    def update_card(self, karten_nummer, updates):
        cards = self.load_cards()
        for card in cards:
            if card.get("karten_nummer") == karten_nummer:
                card.update(updates)
                card["last_reviewed"] = datetime.now().isoformat()
                return self.save_cards(cards)
        return False