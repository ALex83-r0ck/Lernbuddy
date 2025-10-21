from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.screen import MDScreen
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivy.factory import Factory

# Screens importieren
from screens.eingabe_screen import EingabeScreen
from screens.home_screen import HomeScreen
from screens.stats_screen import StatsScreen
from screens.tutor_screen import TutorScreen
from screens.quiz_screen import QuizScreen
from screens.verwaltungs_screen import VerwaltungScreen

class Main(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None  # Wird in build initialisiert
        self.current_screen = 'home'

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"

        # Lade die .kv-Dateien
        Builder.load_file("screens/home_screen.kv")
        Builder.load_file("screens/eingabe_screen.kv")
        Builder.load_file("screens/stats_screen.kv")
        Builder.load_file("screens/tutor_screen.kv")
        Builder.load_file("screens/quiz_screen.kv")
        Builder.load_file("screens/verwaltungs_screen.kv")
        Builder.load_file("components/navigation_drawer.kv")


        # Erstelle das MDNavigationLayout als Root-Widget
        self.nav_layout = MDNavigationLayout()

        # Erstelle einen neuen MDScreenManager
        self.screen_manager = MDScreenManager()

        # Füge die Screens zum ScreenManager hinzu
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(EingabeScreen(name="eingabe"))
        self.screen_manager.add_widget(StatsScreen(name="stats"))
        self.screen_manager.add_widget(TutorScreen(name="tutor"))
        self.screen_manager.add_widget(QuizScreen(name="quiz"))
        self.screen_manager.add_widget(VerwaltungScreen(name="verwaltung"))

        drawer = Factory.CustomNavigationDrawer()
       
        # Lyout zusammenstellen
        self.nav_layout.add_widget(self.screen_manager)
        self.nav_layout.add_widget(drawer)

        # Setze das Root-Widget
        self.root = self.nav_layout

        #print(f"Root widget: {self.root}, children: {self.root.children}")
        #print(f"Screen manager: {self.screen_manager}, children: {self.screen_manager.children}")

        return self.root

    def on_start(self):
        try:
            # Stelle sicher, dass screen_manager initialisiert ist
            if self.screen_manager is not None:
                self.screen_manager.current = "home"
                print(f"✅ ScreenManager ready, current screen: {self.screen_manager.current}")
            else:
                print("❌ Fehler: screen_manager ist None in on_start")
        except Exception as e:
            print(f"❌ Fehler in on_start: {e}")

    def app_show_snackbar(self, message):
        snackbar = MDSnackbar(text=message, snackbar_x="10dp", snackbar_y="10dp")
        snackbar.open()

    def switch_screen(self, screen_name):
        if self.screen_manager is None:
            print("❌ Fehler: screen_manager ist None")
            return
        if screen_name not in self.screen_manager.screen_names:
            print(f"❌ Fehler: Bildschirm '{screen_name}' existiert nicht im ScreenManager")
            return
        print(f"🔄 Wechsel zu Bildschirm: {screen_name}")
        self.screen_manager.current = screen_name

    def toggle_nav_drawer(self):
        try:
            drawer = self.root.children[0]  # Drawer liegt hinter dem ScreenManager
            if isinstance(drawer, MDNavigationDrawer):
                drawer.set_state("toggle")
            else:
                print("❌ Kein Drawer gefunden!")
        except Exception as e:
            print(f"❌ Fehler in toggle_nav_drawer: {e}")


if __name__ == "__main__":
    Main().run()