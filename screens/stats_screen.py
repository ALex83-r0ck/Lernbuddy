# screens/stats_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from utils.json_handler import CardStorage

class StatsScreen(MDScreen):
    def on_enter(self):
        self.update_stats()

    def update_stats(self):
        storage = CardStorage()
        cards = storage.load_cards()
        total = len(cards)
        rot = sum(1 for c in cards if c["difficulty"] == "rot")
        gelb = sum(1 for c in cards if c["difficulty"] == "gelb")
        grün = sum(1 for c in cards if c["difficulty"] == "grün")
        neu = total - rot - gelb - grün

        self.ids.stats.clear_widgets()
        self.add_stat("Neu", neu, [0.7, 0.7, 0.7, 1])
        self.add_stat("Rot (schwer)", rot, [0.8, 0.1, 0.1, 1])
        self.add_stat("Gelb (mittel)", gelb, [0.9, 0.7, 0.1, 1])
        self.add_stat("Grün (leicht)", grün, [0.1, 0.7, 0.1, 1])
        self.ids.total.text = f"Gesamt: {total} Karten"

    def add_stat(self, label, count, color):
        box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            padding=dp(10)
        )
        box.add_widget(MDLabel(
            text=f"{label}: {count}",
            theme_text_color="Custom",
            text_color=color,
            font_style="H6"
        ))
        self.ids.stats.add_widget(box)