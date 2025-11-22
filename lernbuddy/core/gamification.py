# utils/gamification.py
import json
import os
from datetime import datetime, date

GAMIFICATION_FILE = "data/gamification.json"

class Gamification:
    def __init__(self):
        self.data = self.load()

    def load(self):
        if os.path.exists(GAMIFICATION_FILE):
            with open(GAMIFICATION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "points": 0,
            "level": 1,
            "streak": 0,
            "last_active": None,
            "badges": [],
            "history": []
        }

    def save(self):
        with open(GAMIFICATION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def add_points(self, points):
        self.data["points"] += points
        self.data["level"] = self.data["points"] // 100 + 1
        self.check_badges()
        self.save()

    def update_streak(self):
        today = date.today().isoformat()
        last = self.data["last_active"]

        if last == today:
            return  # Schon heute aktiv

        if last is None:
            self.data["streak"] = 1
        else:
            last_date = datetime.fromisoformat(last).date()
            if (date.today() - last_date).days == 1:
                self.data["streak"] += 1
            else:
                self.data["streak"] = 1

        self.data["last_active"] = today
        self.check_badges()
        self.save()

    def check_badges(self):
        badges = [
            {"id": "first_card", "name": "Erste Karte", "desc": "Erstelle deine erste Lernkarte", "icon": "card-plus"},
            {"id": "10_cards", "name": "10 Karten", "desc": "Erstelle 10 Karten", "icon": "cards"},
            {"id": "3_streak", "name": "3 Tage Streak", "desc": "Lerne 3 Tage hintereinander", "icon": "fire"},
            {"id": "7_streak", "name": "1 Woche Streak", "desc": "Lerne 7 Tage hintereinander", "icon": "medal"},
            {"id": "level_5", "name": "Level 5", "desc": "Erreiche Level 5", "icon": "trophy"},
            {"id": "quiz_master", "name": "Quiz-Meister", "desc": "Beantworte 50 Fragen richtig", "icon": "brain"},
        ]

        earned = []
        total_cards = len([h for h in self.data["history"] if h["action"] == "add_card"])
        total_correct = sum(h["points"] for h in self.data["history"] if h["action"] == "correct_answer")

        for badge in badges:
            if badge["id"] not in self.data["badges"]:
                if (badge["id"] == "first_card" and total_cards >= 1) or \
                   (badge["id"] == "10_cards" and total_cards >= 10) or \
                   (badge["id"] == "3_streak" and self.data["streak"] >= 3) or \
                   (badge["id"] == "7_streak" and self.data["streak"] >= 7) or \
                   (badge["id"] == "level_5" and self.data["level"] >= 5) or \
                   (badge["id"] == "quiz_master" and total_correct >= 50):
                    self.data["badges"].append(badge["id"])
                    earned.append(badge)

        if earned:
            self.save()
        return earned

    def log_action(self, action, points=0):
        self.data["history"].append({
            "date": datetime.now().isoformat(),
            "action": action,
            "points": points
        })
        self.save()