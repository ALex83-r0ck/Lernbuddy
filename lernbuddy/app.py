# main.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import MDSnackbar
from kivy.uix.widget import Widget
import os
import shutil
import json
from pathlib import Path


# Screens importieren
from lernbuddy.screens.login.login_screen import LoginScreen
from lernbuddy.screens.splash.splash_screen import SplashScreen
from lernbuddy.screens.home.home_screen import HomeScreen
from lernbuddy.screens.cardsgenerator.cardsgenerator import EingabeScreen
from lernbuddy.screens.statistik.stats_screen import StatsScreen
from lernbuddy.screens.tutor.tutor_screen import TutorScreen
from lernbuddy.screens.quiz.quiz_screen import QuizScreen
from lernbuddy.screens.setupscreens.quiz.setup_quiz import SetupQuizScreen
from lernbuddy.screens.verwaltung_cards.verwaltungs_screen import VerwaltungScreen

from lernbuddy.ai.ollama_manager import OllamaManager

os.environ["KIVY_CAMERA"] = "opencv"


class LernBuddyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None
        self.root = None
        self.ollama_manager = OllamaManager()
        self.ollama_manager.start()
        return ...

    def build(self):
        # Grundlegendes App-Design
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"

        # KV-Dateien aus screens/ automatisch laden
        for kv_file in Path("screens").glob("*.kv"):
            Builder.load_file(str(kv_file))

        # Root-Layout laden (Navigation Drawer)
        kv_path = "components/navigation_drawer.kv"
        if not os.path.exists(kv_path):
            print(f"FEHLER: {kv_path} nicht gefunden!")
            return Widget()

        self.root = Builder.load_file(kv_path)

        # ScreenManager aus Drawer holen
        if self.root and hasattr(self.root, "ids") and "screen_manager" in self.root.ids:
            self.screen_manager = self.root.ids.screen_manager
        else:
            print("FEHLER: screen_manager nicht in navigation_drawer.kv definiert!")
            return Widget()

        # Screens hinzufügen
        screens = [
            LoginScreen(name="login"),
            SplashScreen(name="splash"),
            HomeScreen(name="home"),
            EingabeScreen(name="eingabe"),
            StatsScreen(name="stats"),
            TutorScreen(name="tutor"),
            QuizScreen(name="quiz"),
            VerwaltungScreen(name="verwaltung"),
        ]
        for screen in screens:
            self.screen_manager.add_widget(screen)

        return self.root

    def on_start(self):
        self.load_theme()
        if isinstance(self.screen_manager, MDScreenManager):
            self.screen_manager.current = "login"

    def on_stop(self):
        """Beim Schließen der App Theme speichern"""
        self.save_theme()
        self.ollama_manager.stop()

    # ------------------------------------------------------------
    # 🔹 Navigation & UI
    # ------------------------------------------------------------

    def switch_screen(self, screen_name: str):
        if (
            self.screen_manager
            and hasattr(self.screen_manager, "screen_names")
            and screen_name in self.screen_manager.screen_names
        ):
            self.screen_manager.current = screen_name
            self.update_nav_active(screen_name)

    def toggle_nav_drawer(self):
        nav_drawer = self.root.ids.get("nav_drawer") if self.root else None
        if nav_drawer and hasattr(nav_drawer, "set_state"):
            nav_drawer.set_state("toggle")

    def update_nav_active(self, screen_name: str):
        """Aktiviert im Drawer den aktuellen Menüpunkt"""
        if not self.root or not hasattr(self.root, "ids"):
            return

        nav_drawer = self.root.ids.get("nav_drawer")
        if not nav_drawer or not hasattr(nav_drawer, "ids"):
            return

        nav_list = nav_drawer.ids.get("nav_list")
        if not nav_list:
            return

        mapping = {
            "home": "home_item",
            "eingabe": "eingabe_item",
            "stats": "stats_item",
            "tutor": "tutor_item",
            "quiz": "quiz_item",
            "verwaltung": "verwaltung_item",
        }

        active_id = mapping.get(screen_name)

        # Alle deaktivieren
        for item in getattr(nav_list, "children", []):
            if hasattr(item, "active"):
                item.active = False

        # Aktuellen aktivieren
        if active_id and active_id in nav_drawer.ids:
            active_item = nav_drawer.ids[active_id]
            if hasattr(active_item, "active"):
                active_item.active = True

    # ------------------------------------------------------------
    # 🔹 Snackbar & Feedback
    # ------------------------------------------------------------

    def app_show_snackbar(self, message: str):
        if not message:
            return
        MDSnackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            duration=3,
            md_bg_color=self.theme_cls.primary_color,
        ).open()

    # ------------------------------------------------------------
    # 🔹 Backup & Daten
    # ------------------------------------------------------------

    def export_backup(self):
        """Sichert alle wichtigen Datenordner als ZIP"""
        try:
            os.makedirs("backup", exist_ok=True)
            shutil.make_archive("backup/lernbuddy_backup", "zip", ".")
            self.app_show_snackbar("Backup erstellt: backup/lernbuddy_backup.zip")
        except Exception as e:
            self.app_show_snackbar(f"Backup fehlgeschlagen: {e}")

    # ------------------------------------------------------------
    # 🔹 Theme-Verwaltung
    # ------------------------------------------------------------

    def toggle_theme(self):
        """Wechselt zwischen Light/Dark Theme"""
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        self.save_theme()

    def save_theme(self):
        """Speichert aktuelle Theme-Einstellung"""
        os.makedirs("data", exist_ok=True)
        try:
            with open("data/settings.json", "w", encoding="utf-8") as f:
                json.dump({"theme": self.theme_cls.theme_style}, f, indent=2)
        except Exception as e:
            print(f"Theme speichern fehlgeschlagen: {e}")

    def load_theme(self):
        """Lädt Theme aus Datei"""
        path = "data/settings.json"
        if not os.path.exists(path):
            self.theme_cls.theme_style = "Light"
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                theme = data.get("theme")
                if theme in ("Light", "Dark"):
                    self.theme_cls.theme_style = theme
        except Exception as e:
            print(f"Themeladen fehlgeschlagen: {e}")


if __name__ == "__main__":
    LernBuddyApp().run()
