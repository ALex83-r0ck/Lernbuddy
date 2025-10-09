import json
import os


class CardStorage:
    def __init__(self, file_path="data/fragen.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Stellt sicher, dass die Datei und das Verzeichnis existieren"""
        # Verzeichnis erstellen falls nötig
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Datei erstellen falls nötig
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"cards": []}, f, indent=2, ensure_ascii=False)

    def load_cards(self):
        """Lädt alle Karten aus der JSON-Datei"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("cards", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_cards(self, cards):
        """Speichert alle Karten in die JSON-Datei"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"cards": cards}, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

    def card_number_exists(self, karten_nummer):
        """Prüft ob eine Kartennummer bereits existiert"""
        cards = self.load_cards()
        return any(card.get("karten_nummer") == karten_nummer for card in cards)

    def add_card(self, card_data):
        """Fügt eine neue Karte hinzu - mit Duplikatsprüfung"""
        cards = self.load_cards()
        
        # Doppelte Kartennummer prüfen
        if self.card_number_exists(card_data.get("karten_nummer")):
            print(f"Warnung: Karte mit Nummer {card_data.get('karten_nummer')} existiert bereits!")
            return False
        
        # Automatische ID-Vergabe
        card_data["id"] = len(cards) + 1
        cards.append(card_data)
        
        return self.save_cards(cards)

    def get_card_by_number(self, karten_nummer):
        """Gibt eine Karte anhand der Kartennummer zurück"""
        cards = self.load_cards()
        for card in cards:
            if card.get("karten_nummer") == karten_nummer:
                return card
        return None

    def delete_card(self, karten_nummer):
        """Löscht eine Karte anhand der Kartennummer"""
        cards = self.load_cards()
        cards = [card for card in cards if card.get("karten_nummer") != karten_nummer]
        return self.save_cards(cards)

    def update_card(self, karten_nummer, updated_data):
        """Aktualisiert eine bestehende Karte"""
        cards = self.load_cards()
        for i, card in enumerate(cards):
            if card.get("karten_nummer") == karten_nummer:
                cards[i].update(updated_data)
                return self.save_cards(cards)
        return False