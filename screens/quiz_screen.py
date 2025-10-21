# screens/quiz_screen.py (vollständiger Code – ersetze deinen)
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from utils.json_handler import CardStorage
from datetime import datetime
import ollama
import random
import threading  # Für async Ollama

class QuizScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_cache = {}  # Performance: Karten cachen

    def on_enter(self):
        self.storage = CardStorage()
        self.cards = self.storage.load_cards()  # Einmal laden
        self.start_quiz()

    def start_quiz(self):
        # Custom: Später Input für Anzahl + Zeit
        self.num_questions = 40
        self.time_total = 90 * 60  # 90 Min in Sek

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
        card = self.questions[self.current]
        self.ids.question.text = f"Frage {self.current + 1}/{len(self.questions)}\n{card['question']}"
        self.ids.answer.text = ""
        # MC-Option (siehe Punkt 2)
        if card.get("multiple_choice"):
            self.show_multiple_choice(card["multiple_choice"])

    def show_multiple_choice(self, options):
        # Später implementieren (siehe Punkt 2)
        pass

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
        self.ids.question.text += "\n\nBewertung lädt..."  # Feedback
        threading.Thread(target=self.evaluate_async, args=(card, user)).start()  # Async!

    def evaluate_async(self, card, user):
        correct = self.evaluate_with_ollama(card, user)
        Clock.schedule_once(lambda dt: self.process_evaluation(card, correct))

    def process_evaluation(self, card, correct):
        if correct:
            card["correct_streak"] += 1
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
        prompt = f"Prüfungsmodus. Nur JA oder NEIN.\nFrage: {card['question']}\nKorrekte: {card['answer']['detailed']}\nAntwort: {user_answer}\nRichtig? JA/NEIN"
        response = ollama.generate(model='llama3.1:8b', prompt=prompt)
        return "JA" in response['response'].upper()

    def end_quiz(self):
        if hasattr(self, 'timer'):
            self.timer.cancel()
        self.ids.question.text = f"Fertig! {self.score}/{len(self.questions)} richtig"
        self.ids.answer.disabled = True
        # History speichern (siehe Punkt 4)
        self.save_quiz_history()

    def save_quiz_history(self):
        # Später (Punkt 4)
        pass