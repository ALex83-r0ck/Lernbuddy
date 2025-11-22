# screens/splash_screen.py
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from datetime import datetime
import subprocess
from kivymd.app import MDApp


class SplashScreen(MDScreen):
    def on_enter(self):
        username = self.manager.get_screen("login").ids.username.text or "Gast"
        self.ids.welcome.text = f"Willkommen, {username}!"

        self.start_ollama()

        # Uhr alle 1 Sekunde aktualisieren
        self.clock_event = Clock.schedule_interval(self.update_clock, 1)
        # Nach 2,5 Sekunden weiter zur Home-Screen
        Clock.schedule_once(self.go_to_home, 2.5)

    def update_clock(self, dt):
        self.ids.clock.text = datetime.now().strftime("%H:%M:%S")

    def start_ollama(self):
        try:
            # Nutze String mit shell=True oder Liste ohne shell
            subprocess.Popen("ollama serve", shell=True)
            self.ids.status.text = "Ollama startet..."
        except Exception as e:
            self.ids.status.text = "Ollama-Start fehlgeschlagen."
            print(f"Ollama konnte nicht gestartet werden: {e}")

    def go_to_home(self, dt):
        # Stoppe die Uhr
        if hasattr(self, "clock_event"):
            self.clock_event.cancel()
        self.manager.current = "home"
