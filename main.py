from kivymd.app import MDApp as App
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivymd.uix.button import MDFabButton
from kivymd.theming import ThemeManager

# Screens importieren
from screens.eingabe_screen import EingabeScreen
from screens.home_screen import HomeScreen
from screens.stats_screen import StatsScreen
from screens.tutor_screen import TutorScreen
from screens.quiz_screen import QuizScreen

class Lernkarten(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = MDScreenManager() 
        self.current_screen = 'home'

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        print(f"Primary palette: {self.theme_cls.primary_palette}")  # Debug
        print(f"ThemeManager attributes: {dir(self.theme_cls)}")  # Debug
        Builder.load_file("screens/home_screen.kv")
        Builder.load_file("screens/eingabe_screen.kv")
        Builder.load_file("screens/stats_screen.kv")
        Builder.load_file("screens/tutor_screen.kv")
        Builder.load_file("screens/quiz_screen.kv")
        return Builder.load_file("main.kv")  # Aktualisiert zu main.kv

    def on_start(self):
        try:
            self.screen_manager = self.root
            self.screen_manager.current = "home"
            print(f"✅ ScreenManager ready, current screen: {self.screen_manager.current}")
            print(f"Root: {self.root}")
            print(f"Root children: {self.root.children}")
        except Exception as e:
            print(f"❌ Fehler in on_start: {e}")

if __name__ == "__main__":
    Lernkarten().run()