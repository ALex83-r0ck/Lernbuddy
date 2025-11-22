# coding=utf-8
# screens/tutor_screen.py
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton
from ai.tutor_chatbot import ChatbotTutor


class TutorScreen(MDScreen):
    """Chat-Screen für den KI-Lern-Tutor (Ollama oder Offline-Modus)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = ChatbotTutor()
        self.loading_widget = None

    def on_pre_enter(self):
        Clock.schedule_once(self._add_welcome_message, 0.2)

    # -------------------------------------------------------
    # Nachrichtensystem
    # -------------------------------------------------------
    def _add_welcome_message(self, *args):
        """Begrüßungsnachricht beim Betreten des Screens."""
        welcome = (
            "👋 Hey Azubi! Ich bin dein KI-Tutor für AP1, AP2, WISO, Recht & HGB.\n"
            "Frag mich einfach was – ich erkläre es kurz, klar & witzig 😄"
        )
        self.add_message(welcome, is_user=False)

    def send_message(self, *args):
        """Sendet eine Nutzernachricht und startet KI-Antwort."""
        text = self.ids.input_field.text.strip()
        if not text:
            return

        self.ids.input_field.text = ""
        self.add_message(text, is_user=True)

        # Ladeindikator
        self.loading_widget = self.add_message("Denke nach...", is_user=False)
        self.scroll_to_bottom()

        # Antwort abrufen (async)
        def callback(answer):
            if self.loading_widget and self.loading_widget.parent:
                self.ids.chat_box.remove_widget(self.loading_widget)
            self.add_message(answer, is_user=False)
            self.scroll_to_bottom()

        self.chatbot.ask(text, callback)

    # -------------------------------------------------------
    # Chat-Rendering
    # -------------------------------------------------------
    def add_message(self, text: str, is_user: bool):
        """Fügt eine Chatnachricht hinzu (als Blase mit Text)."""
        chat_box = self.ids.chat_box

        # Chatblase
        bubble = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            padding=[dp(12), dp(10)],
            md_bg_color=(0.1, 0.5, 1, 1) if is_user else (0.93, 0.93, 0.93, 1),
            radius=[dp(20), dp(20), dp(6) if is_user else dp(20), dp(20) if is_user else dp(6)],
            adaptive_height=True,
        )

        label = MDLabel(
            text=text,
            markup=True,
            halign="left",
            theme_text_color="Primary",
            text_size=(dp(280), None),
            size_hint_y=None,
            padding=[dp(8), dp(8)],
        )
        label.bind(texture_size=lambda *_: setattr(label, "height", label.texture_size[1] + dp(16)))
        bubble.add_widget(label)

        # Container (zum Ausrichten links/rechts)
        container = MDBoxLayout(
            size_hint_y=None,
            padding=[dp(50), dp(4), dp(50), dp(4)],
            adaptive_height=True,
        )

        if is_user:
            container.add_widget(MDBoxLayout())  # Platzhalter links
            container.add_widget(bubble)
        else:
            container.add_widget(bubble)
            container.add_widget(MDBoxLayout())  # Platzhalter rechts

        chat_box.add_widget(container)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.05)
        return container

    def scroll_to_bottom(self):
        """Scrollt automatisch ans Ende des Chats."""
        scroll = self.ids.scroll_view
        Clock.schedule_once(lambda dt: setattr(scroll, "scroll_y", 0))

