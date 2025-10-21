# screens/quiz_screen.py
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from utils.json_handler import CardStorage
from kivymd.uix.button import MDRaisedButton
from kivymd.color_definitions import colors
from kivy.metrics import dp
from datetime import datetime
import ollama
import random
import threading
import json
import os

class QuizScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_cache = {}

    def on_enter(self):
        Clock.schedule_once(self._after_enter, 0.1)

    def _after_enter(self, dt):
        self.storage = CardStorage()
        self.cards = self.storage.load_cards()
        self.start_quiz()

    def start_quiz(self):
        # Custom Settings: Später Dialog
        self.num_questions = 40
        self.time_total = 90 * 60

        questions = [c for c in self.cards if c["difficulty"] in [None, "rot", "gelb"]]
        if not questions:
            self.ids.question.text = "Alle Karten grün! Super!"
            return

        random.shuffle(questions)
        self.questions = questions[:self.num_questions]
        self.current = 0
        self.score = 0
        self.time_left = self.time_total
        self.ids.timer.text = f"{self.time_total // 60:02d}:00"
        self.show_question()
        self.start_timer()

    def show_question(self):
        if self.current >= len(self.questions):
            self.end_quiz()
            return

        card = self.questions[self.current]
        self.ids.question.text = f"Frage {self.current + 1}/{len(self.questions)}\n\n{card['question']}"
        self.ids.answer.text = ""

        # Multiple Choice?
        if card.get("multiple_choice"):
            self.show_multiple_choice(card["multiple_choice"])
        else:
            self.hide_multiple_choice()

    def show_multiple_choice(self, mc_data):
        options = mc_data["options"]
        correct = mc_data["correct"]
        self.current_mc_correct = correct

        # Leere alte Chips
        self.ids.mc_grid.clear_widgets()

        for i, opt in enumerate(options):
            chip = MDRaisedButton(
                text=opt,
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x, idx=i: self.select_mc(idx)
            )
            self.ids.mc_grid.add_widget(chip)

        self.ids.mc_container.opacity = 1
        self.ids.mc_container.disabled = False

    def hide_multiple_choice(self):
        self.ids.mc_container.opacity = 0
        self.ids.mc_container.disabled = True

    def select_mc(self, idx):
        if hasattr(self, 'current_mc_correct') and idx == self.current_mc_correct:
            self.process_evaluation(self.questions[self.current], True)
        else:
            self.process_evaluation(self.questions[self.current], False)

    def start_timer(self):
        self.timer = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        m, s = divmod(self.time_left, 60)
        self.ids.timer.text = f"{m:02d}:{s:02d}"
        if self.time_left <= 0:
            self.end_quiz()

    def submit(self):
        user = self.ids.answer.text.strip()
        if not user:
            return
        card = self.questions[self.current]
        self.ids.question.text += "\n\nBewertung lädt..."
        threading.Thread(target=self.evaluate_async, args=(card, user)).start()

    def evaluate_async(self, card, user):
        correct = self.evaluate_with_ollama(card, user)
        Clock.schedule_once(lambda dt: self.process_evaluation(card, correct))

    def process_evaluation(self, card, correct):
        if correct:
            card["correct_streak"] = card.get("correct_streak", 0) + 1
            if card["correct_streak"] >= 3:
                card["difficulty"] = "grün"
            elif card["correct_streak"] >= 1:
                card["difficulty"] = "gelb"
            self.score += 1
        else:
            card["correct_streak"] = 0
            card["difficulty"] = "rot"

        card["last_reviewed"] = datetime.now().isoformat()
        self.storage.update_card(card["karten_nummer"], card)

        self.current += 1
        if self.current < len(self.questions):
            self.show_question()
        else:
            self.end_quiz()

    def evaluate_with_ollama(self, card, user_answer):
        prompt = f"""
        Prüfungsmodus. Nur JA oder NEIN.
        Frage: {card['question']}
        Korrekte Antwort: {card['answer']['detailed']}
        Azubi-Antwort: {user_answer}
        Ist die Antwort im Kern richtig? Antworte NUR mit "JA" oder "NEIN".
        """
        try:
            response = ollama.generate(model='llama3.1:8b', prompt=prompt)
            return "JA" in response['response'].upper()
        except:
            return False

    def end_quiz(self):
        if hasattr(self, 'timer'):
            self.timer.cancel()
        self.ids.question.text = f"Prüfung beendet!\n\n{self.score}/{len(self.questions)} richtig ({self.score/len(self.questions)*100:.1f}%)"
        self.ids.answer.disabled = True
        self.save_quiz_history()

    def save_quiz_history(self):
        history = {
            "date": datetime.now().isoformat(),
            "score": self.score,
            "total": len(self.questions),
            "percentage": round(self.score / len(self.questions) * 100, 1),
            "questions": [q["karten_nummer"] for q in self.questions]
        }
        os.makedirs("data", exist_ok=True)
        with open("data/quiz_history.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(history, ensure_ascii=False) + "\n")