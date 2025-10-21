from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineRightIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from utils.json_handler import CardStorage


class VerwaltungScreen(MDScreen):
    def on_pre_enter(self):
        """Wird aufgerufen, wenn der Screen angezeigt wird."""
        self.load_cards()

    def load_cards(self):
        """Lädt alle Karten und zeigt sie in der Liste an."""
        storage = CardStorage()
        cards = storage.load_cards()

        cards_list = self.ids.cards_list
        cards_list.clear_widgets()

        if not cards:
            from kivymd.uix.label import MDLabel
            cards_list.add_widget(MDLabel(text="Keine Karten vorhanden.", halign="center"))
            return

        for card in cards:
            item = TwoLineRightIconListItem(
                text=f"Karte {card['karten_nummer']} | {card['theme']}",
                secondary_text=f"Lernfeld: {card.get('lernfeld', 'N/A')}",
                on_release=lambda x, c=card: self.edit_card(c)
            )

            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, c=card: self.confirm_delete(c)
            )
            item.add_widget(delete_btn)

            cards_list.add_widget(item)

    def confirm_delete(self, card):
        """Zeigt Bestätigungsdialog vor dem Löschen."""
        self.dialog = MDDialog(
            title="Löschen bestätigen",
            text=f"Möchten Sie die Karte {card['karten_nummer']} wirklich löschen?",
            buttons=[
                MDFlatButton(text="Abbrechen", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="Löschen",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self.delete_card(card)
                ),
            ],
        )
        self.dialog.open()

    def delete_card(self, card):
        """Löscht die Karte aus der JSON-Datei."""
        storage = CardStorage()
        success = storage.delete_card(card["karten_nummer"])

        self.dialog.dismiss()

        if success:
            self.load_cards()

    def edit_card(self, card):
        """Öffnet EingabeScreen mit vorausgefüllten Daten."""
        eingabe_screen = self.manager.get_screen("eingabe")
        eingabe_screen.ids.themengebiet.text = card["theme"]
        eingabe_screen.ids.karten_nummer.text = str(card["karten_nummer"])
        eingabe_screen.ids.frage.text = card["question"]
        eingabe_screen.ids.antwort_kurz.text = card["answer"]["simple"]
        eingabe_screen.ids.antwort_detail.text = card["answer"]["detailed"]
        eingabe_screen.selected_category = card.get("lernfeld", "")

        # Chips aktualisieren
        eingabe_screen.set_category(eingabe_screen.selected_category)

        self.manager.current = "eingabe"

