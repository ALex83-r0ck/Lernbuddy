from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineRightIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.clock import Clock
from utils.json_handler import CardStorage
import logging

logging.basicConfig(level=logging.INFO, format="[VerwaltungScreen] %(message)s")


class VerwaltungScreen(MDScreen):
    """Screen zur Verwaltung, Bearbeitung und Löschung von Lernkarten."""

    def on_pre_enter(self):
        """Beim Betreten: Karten nach kurzer Verzögerung laden (UI ready)."""
        Clock.schedule_once(lambda dt: self.load_cards(), 0.1)

    # ---------------------------------------------------------------------
    # Karten laden
    # ---------------------------------------------------------------------
    def load_cards(self):
        """Lädt alle gespeicherten Lernkarten und rendert sie in der Liste."""
        storage = CardStorage()
        cards = storage.load_cards()
        cards_list = self.ids.cards_list
        cards_list.clear_widgets()

        if not cards:
            cards_list.add_widget(
                MDLabel(
                    text="Keine Karten vorhanden.",
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(60),
                    font_style="Subtitle1",
                )
            )
            logging.info("Keine Karten im Speicher gefunden.")
            return

        for card in cards:
            item = TwoLineRightIconListItem(
                text=f"{card.get('theme', 'Unbekannt')} (#{card.get('karten_nummer', '?')})",
                secondary_text=f"Lernfeld: {card.get('lernfeld', '—')}",
                on_release=lambda x, c=card: self.edit_card(c),
            )

            # ✏️ Edit-Button
            item.add_widget(
                IconRightWidget(
                    icon="pencil-outline",
                    theme_text_color="Custom",
                    text_color=(0.2, 0.4, 0.9, 1),
                    on_release=lambda x, c=card: self.edit_card(c),
                )
            )

            # 🗑️ Delete-Button
            item.add_widget(
                IconRightWidget(
                    icon="trash-can-outline",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x, c=card: self.confirm_delete(c),
                )
            )

            cards_list.add_widget(item)

        logging.info(f"{len(cards)} Karten erfolgreich geladen.")

    # ---------------------------------------------------------------------
    # Karte löschen (mit Bestätigung)
    # ---------------------------------------------------------------------
    def confirm_delete(self, card):
        """Fragt den Nutzer, ob er eine Karte löschen will."""
        if hasattr(self, "delete_dialog") and self.delete_dialog:
            self.delete_dialog.dismiss(force=True)

        self.delete_dialog = MDDialog(
            title="Karte löschen?",
            text=f"Karte #{card.get('karten_nummer', '?')} – '{card.get('theme', 'Unbekannt')}'\n\nWirklich löschen?",
            buttons=[
                MDFlatButton(
                    text="Abbrechen",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    on_release=lambda x: self.delete_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="Löschen",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self._delete_confirmed(card),
                ),
            ],
            radius=[dp(16)] * 4,
        )
        self.delete_dialog.open()

    def _delete_confirmed(self, card):
        """Wird aufgerufen, wenn der Nutzer das Löschen bestätigt."""
        storage = CardStorage()
        success = storage.delete_card(card)
        self.delete_dialog.dismiss()

        if success:
            self.load_cards()
            self._show_snackbar("Karte gelöscht 🗑️")
            logging.info(f"Karte #{card.get('karten_nummer')} gelöscht.")
        else:
            self._show_snackbar("Fehler beim Löschen ❌")
            logging.error("Fehler beim Löschen der Karte.")

    # ---------------------------------------------------------------------
    # Karte bearbeiten
    # ---------------------------------------------------------------------
    def edit_card(self, card):
        """Öffnet die Eingabe-Screen und überträgt Kartendaten."""
        app = self.manager.parent.app if self.manager and self.manager.parent else None
        if not app:
            logging.error("App-Referenz nicht gefunden.")
            return

        try:
            screen_manager = app.root.ids.screen_manager
            eingabe = screen_manager.get_screen("eingabe")
        except Exception as e:
            logging.error(f"Konnte Eingabe-Screen nicht finden: {e}")
            return

        # 🧾 Daten übertragen
        eingabe.ids.themengebiet.text = card.get("theme", "")
        eingabe.ids.karten_nummer.text = str(card.get("karten_nummer", ""))
        eingabe.ids.frage.text = card.get("question", "")
        answer = card.get("answer", {})
        eingabe.ids.antwort_kurz.text = answer.get("simple", "")
        eingabe.ids.antwort_detail.text = answer.get("detailed", "")
        eingabe.selected_category = card.get("lernfeld", "")

        if hasattr(eingabe, "set_category"):
            eingabe.set_category(eingabe.selected_category)

        # 🖼️ Bild & Tabelle laden (falls vorhanden)
        self._restore_image_and_table(eingabe, card)
        app.switch_screen("eingabe")

    def _restore_image_and_table(self, eingabe, card):
        """Hilfsfunktion: Wiederherstellen von Bild oder Tabelle."""
        # Bild
        if card.get("has_image") and card.get("image_url"):
            eingabe.selected_image_data_uri = card["image_url"]
            eingabe.ids.image_preview_label.text = "Bild geladen ✅"
            eingabe.ids.checkbox_image.active = True
            eingabe.ids.image_container.opacity = 1
            eingabe.ids.image_container.disabled = False

        # Tabelle
        if card.get("has_table") and card.get("table"):
            eingabe.ids.table_grid.clear_widgets()
            headers, *rows = card["table"]

            for header in headers:
                eingabe.ids.table_grid.add_widget(
                    MDLabel(
                        text=header, bold=True, halign="center",
                        size_hint_y=None, height=dp(40)
                    )
                )

            for row in rows:
                for cell in row:
                    eingabe.ids.table_grid.add_widget(
                        MDTextField(text=cell, size_hint_y=None, height=dp(40))
                    )

            eingabe.ids.checkbox_table.active = True
            eingabe.ids.table_grid.opacity = 1
            eingabe.ids.table_grid.disabled = False

    # ---------------------------------------------------------------------
    # Helferfunktionen
    # ---------------------------------------------------------------------
    def _show_snackbar(self, text):
        """Snackbar-Anzeige über die App."""
        try:
            self.parent.parent.app.app_show_snackbar(text)
        except Exception:
            logging.warning(f"Snackbar: {text}")
