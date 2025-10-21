# screens/verwaltung_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineRightIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.color_definitions import colors
from kivy.metrics import dp
from kivy.clock import Clock
from utils.json_handler import CardStorage


class VerwaltungScreen(MDScreen):
    def on_pre_enter(self):
        Clock.schedule_once(lambda dt: self.load_cards(), 0.1)

    def load_cards(self):
        storage = CardStorage()
        cards = storage.load_cards()
        cards_list = self.ids.cards_list
        cards_list.clear_widgets()

        if not cards:
            empty = MDLabel(
                text="Keine Karten vorhanden.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60),
                font_style="Subtitle1"
            )
            cards_list.add_widget(empty)
            return

        for card in cards:
            # Formatierung
            lernfeld = card.get("lernfeld", "Unbekannt")
            theme = card["theme"]
            nummer = card["karten_nummer"]

            item = TwoLineRightIconListItem(
                text=f"Karte {nummer} | {theme}",
                secondary_text=f"Lernfeld: {lernfeld}",
                on_release=lambda x, c=card: self.edit_card(c)
            )

            # Delete-Icon
            delete_icon = IconRightWidget(
                icon="trash-can-outline",
                theme_text_color="Custom",
                text_color=(0.9, 0.2, 0.2, 1),
                on_release=lambda x, c=card: self.confirm_delete(c)
            )
            item.add_widget(delete_icon)

            cards_list.add_widget(item)

    def confirm_delete(self, card):
        self.delete_dialog = MDDialog(
            title="Karte löschen?",
            text=f"Karte {card['karten_nummer']} »{card['theme']}«\nwird unwiderruflich gelöscht.",
            buttons=[
                MDFlatButton(
                    text="Abbrechen",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Löschen",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self.delete_card(card)
                )
            ],
            radius=[dp(16), dp(16), dp(16), dp(16)]
        )
        self.delete_dialog.open()

    def delete_card(self, card):
        storage = CardStorage()
        success = storage.delete_card(card["karten_nummer"])
        self.delete_dialog.dismiss()
        if success:
            self.load_cards()  # Refresh

    def edit_card(self, card):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app and app.root:
            eingabe = app.root.get_screen("eingabe")

        # Daten setzen
        eingabe.ids.themengebiet.text = card["theme"]
        eingabe.ids.karten_nummer.text = str(card["karten_nummer"])
        eingabe.ids.frage.text = card["question"]
        eingabe.ids.antwort_kurz.text = card["answer"]["simple"]
        eingabe.ids.antwort_detail.text = card["answer"]["detailed"]
        eingabe.selected_category = card.get("lernfeld", "")

        # Chips aktualisieren
        if hasattr(eingabe, "set_category"):
            eingabe.set_category(eingabe.selected_category)

        # Wechseln
        if app is not None:
            app.switch_screen("eingabe")