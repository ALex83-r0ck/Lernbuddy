from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.chip import MDChip, MDChipText
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.animation import Animation
from utils.json_handler import CardStorage

class EingabeScreen(MDScreen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
    def on_pre_enter(self):
        """Update die TopAppBar mit Kartenanzahl, wenn Screen angezeigt wird."""
        storage = CardStorage()
        count = len(storage.load_cards())
        if hasattr(self.ids, "top_bar"):
            self.ids.top_bar.title = f"Lernkarten erstellen (Gespeicherte Fragen: {count})"

    def show_message(self, title, message, color="error"):
        """Zeigt eine benutzerfreundliche Nachricht mit Icons als Dialog"""
        if self.dialog:
            self.dialog.dismiss()

        # Konfiguration je nach Typ - mit MDIcons!
        config = {
            "error": {
                "icon": "alert-circle",  # Material Design Icon
                "emoji": "❌",
                "bg_color": [1, 0.95, 0.95, 1],
                "title_color": [0.8, 0.1, 0.1, 1],
                "text_color": [0.3, 0.1, 0.1, 1],
                "icon_color": [0.9, 0.2, 0.2, 1],
                "button_color": [0.9, 0.2, 0.2, 1]
            },
            "success": {
                "icon": "check-circle",
                "emoji": "✅",
                "bg_color": [0.95, 1, 0.95, 1],
                "title_color": [0.1, 0.6, 0.1, 1],
                "text_color": [0.1, 0.3, 0.1, 1],
                "icon_color": [0.2, 0.7, 0.2, 1],
                "button_color": [0.2, 0.7, 0.2, 1]
            },
            "warning": {
                "icon": "alert",
                "emoji": "⚠️",
                "bg_color": [1, 0.98, 0.9, 1],
                "title_color": [0.8, 0.5, 0.1, 1],
                "text_color": [0.4, 0.2, 0.05, 1],
                "icon_color": [0.95, 0.6, 0.1, 1],
                "button_color": [0.95, 0.6, 0.1, 1]
            }
        }
        
        cfg = config.get(color, config["error"])
        
        # Custom Content mit Icon
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(180)
        )
        content.md_bg_color = cfg["bg_color"]
        
        # Header Box (Icon + Titel nebeneinander)
        header_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )
        
        # OPTION 1: Material Design Icon (KivyMD)
        from kivymd.uix.label import MDIcon
        icon_widget = MDIcon(
            icon=cfg["icon"],
            theme_text_color="Custom",
            text_color=cfg["icon_color"],
            font_size="48sp"
        )
        
        # Titel
        title_label = MDLabel(
            text=title,
            font_style="H6",
            halign="left",
            valign="middle",
            theme_text_color="Custom",
            text_color=cfg["title_color"]
        )
        
        header_box.add_widget(icon_widget)
        header_box.add_widget(title_label)
        
        # Nachricht mit Emojis
        message_label = MDLabel(
            text=f"{cfg['emoji']} {message}",
            halign="left",
            size_hint_y=None,
            height=dp(90),
            theme_text_color="Custom",
            text_color=cfg["text_color"]
        )
        
        content.add_widget(header_box)
        content.add_widget(message_label)
        
        # Dialog
        dialog = MDDialog(
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=cfg["button_color"],
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        self.dialog = dialog
        dialog.open()

    def save_card(self):
        # Felder auslesen
        themengebiet = self.ids.themengebiet.text.strip()
        karten_nummer = self.ids.karten_nummer.text.strip()
        frage = self.ids.frage.text.strip()
        antwort_kurz = self.ids.antwort_kurz.text.strip()
        antwort_detail = self.ids.antwort_detail.text.strip()
        has_table = self.ids.checkbox_table.active
        has_image = self.ids.checkbox_image.active
        lernfeld = self.selected_category if hasattr(self, 'selected_category') else ""
        

        # VALIDIERUNG 1: Pflichtfelder prüfen
        if not themengebiet:
            self.show_message("Fehler", "Bitte geben Sie ein Themengebiet ein.", "error")
            self.ids.themengebiet.focus = True
            return
        
        if not karten_nummer:
            self.show_message("Fehler", "Bitte geben Sie eine Kartennummer ein.", "error")
            self.ids.karten_nummer.focus = True
            return
        
        if not frage:
            self.show_message("Fehler", "Bitte geben Sie eine Frage ein.", "error")
            self.ids.frage.focus = True
            return
        
        # VALIDIERUNG 2: Kartennummer muss eine Zahl sein
        try:
            karten_nummer_int = int(karten_nummer)
            if karten_nummer_int <= 0:
                raise ValueError
        except ValueError:
            self.show_message(
                "Ungültige Eingabe", 
                "Die Kartennummer muss eine positive ganze Zahl sein.", 
                "error"
            )
            self.ids.karten_nummer.focus = True
            return
        
        # VALIDIERUNG 3: Duplikat-Prüfung
        storage = CardStorage()
        
        if storage.card_number_exists(karten_nummer_int):
            self.show_message(
                "Duplikat gefunden", 
                f"Eine Karte mit der Nummer {karten_nummer_int} existiert bereits!\n\n"
                f"Bitte verwenden Sie eine andere Kartennummer.",
                "warning"
            )
            self.ids.karten_nummer.focus = True
            return
        
        # VALIDIERUNG 4: Optional - Warnung wenn keine Antwort
        if not antwort_kurz and not antwort_detail:
            self.show_message(
                "Hinweis", 
                "Sie haben keine Antwort eingegeben.\n\n"
                "Die Karte wird trotzdem gespeichert.",
                "warning"
            )
        
        # Karte erstellen
        card = {
            "karten_nummer": karten_nummer_int,
            "theme": themengebiet,
            "lernfeld": lernfeld,
            "question": frage,
            "answer": {
                "simple": antwort_kurz if antwort_kurz else "",
                "detailed": antwort_detail if antwort_detail else ""
            },
            "mnemonics": [],
            "multiple_choice": [],
            "table": [["Beispiel", "Wert"]] if has_table else [],
            "image_url": "https://example.com/image.png" if has_image else "",
            "has_table": has_table,
            "has_image": has_image
        }
        
        # Karte speichern
        success = storage.add_card(card)
        
        if success:
            # Erfolgreiche Speicherung mit Details
            self.show_message(
                "Erfolgreich", 
                f"Die Karte wurde gespeichert!\n\n"
                f"📝 Nummer: {karten_nummer_int}\n"
                f"📚 Thema: {themengebiet}\n"
                f"❓ Frage: {frage[:40]}...",
                "success"
            )
            
            self.clear_fields()
            self.on_pre_enter()
        else:
            self.show_message(
                "Speicherfehler",
                "Die Karte konnte nicht gespeichert werden.\n\n"
                "Bitte versuchen Sie es erneut.",
                "error"
            )

    def clear_fields(self):
        """Alle Eingabefelder zurücksetzen"""
        for field in ["themengebiet", "karten_nummer", "frage", "antwort_kurz", "antwort_detail"]:
            self.ids[field].text = ""
        self.ids.checkbox_table.active = False
        self.ids.checkbox_image.active = False

    def toggle_checkbox(self, checkbox_name):
        """Nur eine Checkbox aktivieren (Tabelle oder Bild)"""
        if checkbox_name == "table":
            if self.ids.checkbox_table.active:
                self.ids.checkbox_image.active = False
        else:
            if self.ids.checkbox_image.active:
                self.ids.checkbox_table.active = False

    def set_category(self, category):
        self.selected_category = category
        self.ids.themengebiet.text = category

        for chip_id in ["ap1_chip", "ap2_chip", "wiso_chip", "else_chip"]:
            chip = self.ids.get(chip_id)
            if chip:
                if chip.text.lower() == category.lower():
                    chip.md_bg_color = (0, 0.6, 0.9, 1)
                    chip.ids.label.text_color = (1, 1, 1, 1)  # MDChipText nutzen
                else:
                    chip.md_bg_color = (0.0, 0.447, 0.6, 1)
                    chip.ids.label.text_color = (1, 1, 1, 0.7)