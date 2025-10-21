# screens/stats_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.color_definitions import colors
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from utils.json_handler import CardStorage
import json
import os
from datetime import datetime

class StatsScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(self._after_enter, 0.1)

    def _after_enter(self, dt):
        self.update_stats()
        self.load_quiz_history()

    def update_stats(self):
        storage = CardStorage()
        cards = storage.load_cards()
        total = len(cards)
        rot = sum(1 for c in cards if c["difficulty"] == "rot")
        gelb = sum(1 for c in cards if c["difficulty"] == "gelb")
        grün = sum(1 for c in cards if c["difficulty"] == "grün")
        neu = total - rot - gelb - grün

        # --- Gesamtfortschritt ---
        if total > 0:
            progress = (grün / total) * 100
        else:
            progress = 0
        if 'progress_bar' in self.ids:
            self.ids.progress_bar.value = progress
            self.ids.progress_label.text = f"{grün}/{total} Karten gemeistert"
            self.ids.progress_percent.text = f"{progress:.1f}%"

        # --- Stats Karten ---
        if 'stats_container' in self.ids:
            self.ids.stats_container.clear_widgets()
            self.add_stat_card("Neu", neu, [0.7, 0.7, 0.7, 1])
            self.add_stat_card("Rot", rot, [0.8, 0.1, 0.1, 1])
            self.add_stat_card("Gelb", gelb, [0.9, 0.7, 0.1, 1])
            self.add_stat_card("Grün", grün, [0.1, 0.7, 0.1, 1])

        if 'total_label' in self.ids:
            self.ids.total_label.text = f"Gesamt: {total} Karten"

    def add_stat_card(self, label, count, color):
        card = MDCard(
            size_hint_y=None,
            height=dp(80),
            padding=dp(16),
            md_bg_color=[c * 0.85 for c in color],
            radius=[dp(16)],
            ripple_behavior=True,
            elevation=2
        )
        card.add_widget(MDLabel(
            text=f"{label}\n[b][color=#ffffff]{count}[/color][/b]",
            markup=True,
            halign="center",
            font_style="H5"
        ))
        self.ids.stats_container.add_widget(card)

    def load_quiz_history(self):
        if 'history_list' not in self.ids:
            return
        self.ids.history_list.clear_widgets()

        history_file = "data/quiz_history.jsonl"
        if not os.path.exists(history_file):
            self.ids.history_list.add_widget(MDLabel(
                text="Noch keine Prüfungen absolviert.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Body2"
            ))
            return

        with open(history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]
            lines.reverse()

        for line in lines:
            try:
                data = json.loads(line)
                date = datetime.fromisoformat(data["date"]).strftime("%d.%m.%Y %H:%M")
                score = data["score"]
                total = data["total"]
                percent = data["percentage"]

                item = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(56),
                    padding=[dp(8), dp(4)],
                    spacing=dp(12)
                )
                item.add_widget(MDLabel(
                    text=date,
                    size_hint_x=0.45,
                    theme_text_color="Secondary",
                    font_style="Caption"
                ))
                item.add_widget(MDLabel(
                    text=f"{score}/{total}",
                    halign="center",
                    size_hint_x=0.25,
                    font_style="Subtitle1",
                    theme_text_color="Primary"
                ))
                item.add_widget(MDLabel(
                    text=f"{percent}%",
                    halign="right",
                    size_hint_x=0.3,
                    font_style="Subtitle1",
                    theme_text_color="Custom",
                    text_color=[0, 0.7, 0, 1] if percent >= 80 else [0.9, 0.7, 0, 1] if percent >= 60 else [0.8, 0.1, 0.1, 1]
                ))
                self.ids.history_list.add_widget(item)
            except:
                continue