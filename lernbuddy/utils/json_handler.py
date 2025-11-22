# utils/json_handler.py
import json
import os
from datetime import datetime
from typing import List, Dict, Any

DATA_FILE = "data/cards.jsonl"

class CardStorage:
    def __init__(self):
        self.file_path = DATA_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.file_path):
            open(self.file_path, "w").close()

    def _get_key(self, card: Dict) -> str:
        theme = str(card.get("theme", "")).strip().lower()
        num = card.get("karten_nummer", 0)
        return f"{theme}_{num}"

    def _ensure_answer_fields(self, card: Dict):
        # Falls answer fehlt
        if "answer" not in card or not isinstance(card["answer"], dict):
            card["answer"] = {"simple": "", "ultra_simple": [], "detailed": ""}

        card["answer"].setdefault("simple", "")
        card["answer"].setdefault("ultra_simple", [])
        card["answer"].setdefault("detailed", "")

    def load_cards(self) -> List[Dict]:
        cards = []
        if not os.path.exists(self.file_path):
            return cards

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        card = json.loads(line)

                        # Felder immer garantieren
                        self._ensure_answer_fields(card)

                        for field in ["difficulty", "correct_streak", "last_reviewed"]:
                            if field not in card:
                                card[field] = None if field != "correct_streak" else 0

                        cards.append(card)
                    except:
                        continue

        return cards

    def save_cards(self, cards: List[Dict]) -> bool:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                for card in cards:
                    self._ensure_answer_fields(card)
                    f.write(json.dumps(card, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Speichern fehlgeschlagen: {e}")
            return False

    def add_card(self, card_data: Dict) -> bool:
        self._ensure_answer_fields(card_data)

        if self.card_exists(card_data):
            return False

        cards = self.load_cards()
        card_data.setdefault("difficulty", None)
        card_data.setdefault("correct_streak", 0)
        card_data.setdefault("last_reviewed", None)

        cards.append(card_data)
        return self.save_cards(cards)

    def update_card(self, card_data: Dict) -> bool:
        self._ensure_answer_fields(card_data)

        cards = self.load_cards()
        key = self._get_key(card_data)

        for i, c in enumerate(cards):
            if self._get_key(c) == key:
                card_data["last_reviewed"] = datetime.now().isoformat()
                cards[i] = card_data
                return self.save_cards(cards)

        return False

    def card_exists(self, card: Dict) -> bool:
        key = self._get_key(card)
        return any(self._get_key(c) == key for c in self.load_cards())

    def delete_card(self, card_data: Dict) -> bool:
        cards = self.load_cards()
        key = self._get_key(card_data)
        cards = [c for c in cards if self._get_key(c) != key]
        return self.save_cards(cards)

    def get_card_by_key(self, theme: str, num: int):
        key = f"{theme.lower().strip()}_{num}"
        return next((c for c in self.load_cards() if self._get_key(c) == key), None)

    def get_cards_by_theme(self, theme: str) -> List[Dict]:
        t = theme.strip().lower()
        return [
            c for c in self.load_cards()
            if str(c.get("theme", "")).strip().lower() == t
        ]

    def get_cards_by_num(self, num: int) -> List[Dict]:
        return [
            c for c in self.load_cards()
            if c.get("karten_nummer", 0) == num
        ]