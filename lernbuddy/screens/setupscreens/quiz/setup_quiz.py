from kivymd.uix.screen import MDScreen
from utils.json_handler import CardStorage
from kivy.app import App


class SetupQuizScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = CardStorage()
        self.categories = []
        self.on_enter = self.load_categories

    def load_categories(self, *args):
        cards = self.storage.load_cards()
        categories = sorted({c.get("lernfeld") for c in cards if c.get("lernfeld")}, key=lambda x: x if x is not None else "")

        self.categories = categories
        self.ids.category_spinner.values = categories

        if categories:
            self.ids.category_spinner.text = "Kategorie auswählen"

    def confirm_settings(self):
        category = self.ids.category_spinner.text
        mode = self.ids.mode_spinner.text
        num = int(self.ids.questions_slider.value)
        minutes = int(self.ids.time_slider.value)

        if category == "Kategorie auswählen":
            self.ids.status_label.text = "[color=#ff3333]Bitte Kategorie wählen[/color]"
            return

        # Mapping der Modusbezeichnungen
        mode_map = {
            "Übungsquiz": "practice",
            "Einstellungs-Quiz": "rating",
            "Normales Quiz": "standard"
        }

        settings = {
            "category": category,
            "mode": mode_map.get(mode, "standard"),
            "num_questions": num,
            "time_min": minutes
        }

        quiz_screen = App.get_running_app().root.get_screen("quiz")
        quiz_screen.settings = settings
        quiz_screen.mode = settings["mode"]
        quiz_screen.prepare_quiz()

        App.get_running_app().root.current = "quiz"
