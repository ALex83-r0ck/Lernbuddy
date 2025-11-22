# screens/home_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.color_definitions import colors
from kivy.clock import Clock
from utils.json_handler import CardStorage
from lernbuddy.core.gamification import Gamification
from datetime import datetime
import random

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = CardStorage()
        self.motivation_quotes = [
            "Heute ist dein Tag – du schaffst das!",
            "Jede Frage, die du heute lernst, ist ein Punkt in der Prüfung.",
            "Du bist stärker als gestern – und klüger als vorgestern.",
            "Prüfung? Nur ein Level, das du freischaltest.",
            "Dein Lern-Buddy glaubt an dich – und du solltest es auch!"
        ]

    def on_enter(self):
        Clock.schedule_once(self._after_enter, 0.1)
    
    def on_pre_enter(self):
        Clock.schedule_once(self._after_enter, 0.1)

    def _after_enter(self, dt):
        try:
            storage = CardStorage()
            count = len(storage.load_cards())
            gamification = Gamification()
            gamification.update_streak()

            # SICHER: Prüfe, ob ID existiert
            if hasattr(self.ids, "card_count"):
                self.ids.card_count.text = f"{count} Karten"
            if hasattr(self.ids, "streak"):
                self.ids.streak.text = f"Streak: {gamification.data['streak']} Tage"
            if hasattr(self.ids, "level"):
                self.ids.level.text = f"Level {gamification.data['level']} | {gamification.data['points']} Punkte"
            if hasattr(self.ids, "welcome_label"):
                self.ids.welcome_label.text = "Willkommen zurück zu LernBuddy!\nViel Erfolg beim Lernen."

        except Exception as e:
            print(f"[HomeScreen] Fehler in _after_enter: {e}")
        
        Clock.schedule_interval(self.check_reminders, 60)

    def check_reminders(self, dt):
        # Beispiel: Tägliche Erinnerung
        if datetime.now().hour == 18:  # 18 Uhr
            self.show_snackbar("Erinnerung: Heute lernen!")


    def update_clock(self, dt):
        if 'clock_label' in self.ids:
            self.ids.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def update_dashboard(self):
        cards = self.storage.load_cards()
        total = len(cards)
        rot = sum(1 for c in cards if c["difficulty"] == "rot")
        gelb = sum(1 for c in cards if c["difficulty"] == "gelb")
        grün = sum(1 for c in cards if c["difficulty"] == "grün")
        neu = total - rot - gelb - grün

        # --- FORTSCHRITTSBALKENSICHER ---
        if 'progress_bar' in self.ids:
            if total > 0:
                progress = (grün / total) * 100
                self.ids.progress_bar.value = progress
            else:
                self.ids.progress_bar.value = 0

        if 'progress_label' in self.ids:
            self.ids.progress_label.text = f"{grün}/{total} Karten gemeistert"

        # --- STATS MIT MARKUP ---
        if 'stats_rot' in self.ids: self.ids.stats_rot.text = f"[color=#ff0000]{rot}[/color]"
        if 'stats_gelb' in self.ids: self.ids.stats_gelb.text = f"[color=#ffaa00]{gelb}[/color]"
        if 'stats_grün' in self.ids: self.ids.stats_grün.text = f"[color=#00aa00]{grün}[/color]"
        if 'stats_neu' in self.ids: self.ids.stats_neu.text = f"[color=#888888]{neu}[/color]"

        # --- TIPP DES TAGES ---
        weak_cards = [c for c in cards if c["difficulty"] in ["rot", None]]
        if weak_cards and 'tip_label' in self.ids:
            tip = random.choice(weak_cards)
            self.ids.tip_label.text = f"[b]Tipp:[/b] {tip['question'][:100]}..."
            self.ids.tip_sub.text = "Klick hier → direkt ins Quiz!"
        elif 'tip_label' in self.ids:
            self.ids.tip_label.text = "[b]Perfekt![/b] Alle Karten sind grün!"
            self.ids.tip_sub.text = "Du bist bereit für die Prüfung!"

    def show_motivation(self):
        if 'motivation_label' in self.ids:
            quote = random.choice(self.motivation_quotes)
            self.ids.motivation_label.text = f"[i]\"{quote}\"[/i]"

    def start_weak_quiz(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app:
            app.switch_screen("quiz")

    def search_cards(self, text):
        if text.strip():
            # Später: echte Suche
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if app: 
                app.switch_screen("quiz")