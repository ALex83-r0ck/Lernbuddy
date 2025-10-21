# screens/tutor_screen.py
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from ai.tutor_chatbot import ChatbotTutor

class TutorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = ChatbotTutor()

    def on_pre_enter(self):
        Clock.schedule_once(lambda dt: self.add_welcome_message(), 0.1)

    def add_welcome_message(self):
        self.add_message("Hallo! Ich bin dein KI-Tutor. Frag mich zu WISO, Recht oder HGB!", is_user=False)

    def send_message(self, *args):
        if 'input_field' not in self.ids:
            return
        input_field = self.ids.input_field
        text = input_field.text.strip()
        if not text:
            return

        self.add_message(text, is_user=True)
        input_field.text = ""

        Clock.schedule_once(lambda dt: self.get_answer(text), 0.2)

    def get_answer(self, question):
        try:
            answer = self.chatbot.ask(question)
            self.add_message(answer, is_user=False)
        except Exception as e:
            self.add_message(f"Fehler: {e}", is_user=False)

    def add_message(self, text, is_user):
        if 'chat_box' not in self.ids:
            return
        chat_box = self.ids.chat_box

        # --- LABEL ---
        label = MDLabel(
            text=text,
            halign="right" if is_user else "left",
            text_size=(None, None),
            size_hint_y=None,
            padding=[dp(12), dp(8)]
        )

        # --- WICHTIG: Bind an texture_size[1] (Höhe) ---
        def update_height(instance, value):
            if value:
                label.height = value[1] + dp(16)  # Text + Padding
        label.bind(texture_size=update_height)

        # --- BLASENGRÖSSE ---
        bubble = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=label.height,  # Wird von update_height gesetzt
            padding=[dp(12), dp(8)],
            md_bg_color=(0.2, 0.6, 1, 1) if is_user else (0.95, 0.95, 0.95, 1),
            radius=[dp(20), dp(20), dp(4) if is_user else dp(20), dp(4) if is_user else dp(20)],
        )
        bubble.add_widget(label)

        # --- AUSRICHTUNG ---
        msg = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=bubble.height,
            padding=[dp(50), 0] if is_user else [0, 0, dp(50), 0]
        )
        if is_user:
            msg.add_widget(MDBoxLayout())
            msg.add_widget(bubble)
        else:
            msg.add_widget(bubble)
            msg.add_widget(MDBoxLayout())

        chat_box.add_widget(msg)

        # --- SCROLLEN ---
        Clock.schedule_once(lambda dt: self.ids.scroll_view.scroll_to(msg, padding=dp(10)), 0.1)    