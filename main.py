from kivymd.app import MDApp
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

class Main(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = MDScreenManager()  # Initialize screen_manager with an instance of MDScreenManager
        self.current_screen = 'home'

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"
        print(f"Theme style: {self.theme_cls.theme_style}")
        print(f"Material style: {self.theme_cls.material_style}")
        print(f"Primary palette: {self.theme_cls.primary_palette}")  # Debug
        print(f"PrimaryColor value: {self.theme_cls.primaryColor}")  # Debug: Überprüfe Farbwert
        Builder.load_file("screens/home_screen.kv")
        Builder.load_file("screens/eingabe_screen.kv")
        Builder.load_file("screens/stats_screen.kv")
        Builder.load_file("screens/tutor_screen.kv")
        Builder.load_file("screens/quiz_screen.kv")
        root = Builder.load_file("main.kv")
        print(f"Root widget: {root}")  # Debug
        return root

    def on_start(self):
        try:
            self.screen_manager = self.root
            if self.screen_manager is None or not isinstance(self.screen_manager, MDScreenManager):
                print(f"❌ Fehler: self.screen_manager ist kein MDScreenManager, sondern: {self.screen_manager}")
                return
            self.screen_manager.current = "home"
            print(f"✅ ScreenManager ready, current screen: {self.screen_manager.current}")
            print(f"Root: {self.root}")
            if self.root is not None:
                print(f"Root children: {self.root.children}")
            else:
                print("Root is None")
        except Exception as e:
            print(f"❌ Fehler in on_start: {e}")

if __name__ == "__main__":
    Main().run()