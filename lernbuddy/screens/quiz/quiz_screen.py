from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from utils.json_handler import CardStorage
import random


class QuizScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []
        self.current_index = 0
        self.mode = None
        self.settings = {}
        self.timer_event = None
        self.time_left = 0
        self.storage = CardStorage()

    # Wird von SetupQuizScreen aufgerufen
    def prepare_quiz(self):
        category = self.settings.get("category")
        num_questions = self.settings.get("num_questions")
        time_min = self.settings.get("time_min")

        # Fragen nach Kategorie filtern
        all_cards = self.storage.load_cards()
        self.cards = [c for c in all_cards if c.get("lernfeld") == category]

        # Mischen
        random.shuffle(self.cards)

        # Schneiden
        self.cards = self.cards[:num_questions]

        if len(self.cards) == 0:
            self.ids.question_label.text = "[b]Keine Fragen in dieser Kategorie![/b]"
            return

        # Timer vorbereiten
        self.time_left = time_min * 60 if time_min is not None else 0
        if self.timer_event:
            self.timer_event.cancel()

        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

        self.current_index = 0
        self.show_question()

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_left < 0:
            self.finish_quiz()
            return

        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.ids.timer_label.text = f"{minutes:02d}:{seconds:02d}"

    def show_question(self):
        if self.current_index >= len(self.cards):
            self.finish_quiz()
            return

        c = self.cards[self.current_index]
        self.ids.question_label.text = f"[b]{c.get('frage', '---')}[/b]"

        # Buttons setzen
        self.ids.answer_a.text = c.get("antwort_a", "---")
        self.ids.answer_b.text = c.get("antwort_b", "---")
        self.ids.answer_c.text = c.get("antwort_c", "---")
        self.ids.answer_d.text = c.get("antwort_d", "---")

    def select_answer(self, answer_key):
        self.current_index += 1
        self.show_question()

    def finish_quiz(self):
        if self.timer_event:
            self.timer_event.cancel()
        self.ids.question_label.text = "[b]Quiz beendet![/b]"
