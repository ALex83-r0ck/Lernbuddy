# screens/eingabe_screen.py
import os
import base64
import tempfile
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.camera import Camera
from kivy.metrics import dp
from lernbuddy.core.gamification import Gamification
from kivy.clock import Clock

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.checkbox import CheckBox
from utils.json_handler import CardStorage


class EingabeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.filechooser_dialog = None
        self.camera_dialog = None
        self.table_config_dialog = None
        self.table_header_names = []
        self.selected_category = None
        self.selected_image_data_uri = None
        self.previous_themes = []

    def show_dialog(self, title, message, option=["OK"], color="error"):
        self.dialog = MDDialog(title=title, text=message, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dismiss_dialog())])
        if self.dialog:
            self.dialog.open()

    def dismiss_dialog(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    # -------------------------
    # Lifecycle
    # -------------------------
    def on_pre_enter(self):
        Clock.schedule_once(self._after_enter, 0.1)
        self.ids.frage.bind(on_text_validate=self.next_field)

    def next_field(self, instance):
        current = instance
        next_field = self.ids.get(next((k for k, v in self.ids.items() if isinstance(v, MDTextField) and v != current), None))
        if next_field:
            next_field.focus = True

    def on_text(self, instance, value):
        if instance == self.ids.themengebiet:
            self.previous_themes = [t for t in self.previous_themes if t]  # Filtere leere
            if value and value not in self.previous_themes:
                self.previous_themes.append(value)
            # Autovervollständigung (einfach)
            if value and any(t.startswith(value) for t in self.previous_themes):
                instance.text = next(t for t in self.previous_themes if t.startswith(value))

    def _after_enter(self, dt):
        storage = CardStorage()
        count = len(storage.load_cards())
        if hasattr(self.ids, "top_bar"):
            self.ids.top_bar.title = f"Lernkarten erstellen (Gespeichert: {count})"

    # -------------------------
    # Messages
    # -------------------------
    def show_message(self, title, message, color="error"):
        if self.dialog:
            self.dialog.dismiss()

        config = {
            "error": {"icon": "alert-circle", "bg": [1, 0.95, 0.95, 1], "title": [0.8, 0.1, 0.1, 1], "text": [0.3, 0.1, 0.1, 1], "btn": [0.9, 0.2, 0.2, 1]},
            "success": {"icon": "check-circle", "bg": [0.95, 1, 0.95, 1], "title": [0.1, 0.6, 0.1, 1], "text": [0.1, 0.3, 0.1, 1], "btn": [0.2, 0.7, 0.2, 1]},
            "warning": {"icon": "alert", "bg": [1, 0.98, 0.9, 1], "title": [0.8, 0.5, 0.1, 1], "text": [0.4, 0.2, 0.05, 1], "btn": [0.95, 0.6, 0.1, 1]},
        }
        cfg = config.get(color, config["error"])

        content = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        header = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(48))
        icon = MDIcon(icon=cfg["icon"], theme_text_color="Custom", text_color=cfg["title"], font_size="32sp")
        header.add_widget(icon)
        header.add_widget(MDLabel(text=title, font_style="H6", theme_text_color="Custom", text_color=cfg["title"]))
        content.add_widget(header)
        content.add_widget(MDLabel(text=message, theme_text_color="Custom", text_color=cfg["text"]))
        content.add_widget(MDRaisedButton(text="OK", md_bg_color=cfg["btn"], on_release=lambda x: dialog.dismiss()))

        dialog = MDDialog(type="custom", content_cls=content)
        self.dialog = dialog
        dialog.open()

    # -------------------------
    # Save Card
    # -------------------------
    def save_card(self):
        themengebiet = self.ids.themengebiet.text.strip()
        karten_nummer = self.ids.karten_nummer.text.strip()
        frage = self.ids.frage.text.strip()
        antwort_kurz = self.ids.antwort_kurz.text.strip()
        antwort_detail = self.ids.antwort_detail.text.strip()
        has_table = self.ids.checkbox_table.active
        has_image = self.ids.checkbox_image.active
        lernfeld = self.selected_category or ""
        gamification = Gamification()
        gamification.log_action("add_card")
        gamification.check_badges()  # Falls "Erste Karte" oder "10 Karten"
        # Rechtschreibung prüfen (Ollama)
        corrected_frage = self.correct_text(frage)
        corrected_kurz =  self.correct_text(antwort_kurz)
        corrected_detail = self.correct_text(antwort_detail)
        frage = corrected_frage
        antwort_kurz = corrected_kurz
        antwort_detail = corrected_detail

        if not themengebiet:
            self.show_message("Fehler", "Bitte Themengebiet eingeben.", "error"); return
        if not karten_nummer:
            self.show_message("Fehler", "Bitte Kartennummer eingeben.", "error"); return
        if not frage:
            self.show_message("Fehler", "Bitte Frage eingeben.", "error"); return

        try:
            karten_nummer_int = int(karten_nummer)
            if karten_nummer_int <= 0:
                raise ValueError
        except ValueError:
            self.show_message("Fehler", "Kartennummer muss positive Zahl sein.", "error"); return

        # Tabelle sammeln
        table = []
        if has_table and hasattr(self, "table_header_names"):
            grid = self.ids.table_grid
            children = [w for w in grid.children if isinstance(w, MDTextField)]
            row = []
            for i, widget in enumerate(children):
                row.append(widget.text.strip())
                if len(row) == len(self.table_header_names):
                    table.append(row)
                    row = []

        # Bild
        image_uri = self.selected_image_data_uri if has_image else ""

        card = {
            "karten_nummer": karten_nummer_int,
            "theme": themengebiet,
            "lernfeld": lernfeld,
            "question": frage,
            "answer": {"simple": antwort_kurz, "detailed": antwort_detail},
            "mnemonics": [],
            "multiple_choice": [],
            "table": table,
            "image_url": image_uri,
            "has_table": bool(table),
            "has_image": bool(image_uri),
        }

        storage = CardStorage()

        if storage.card_exists(card):
            dialog = MDDialog(
                title="Überschreiben?",
                text=f"Karte {karten_nummer_int} in »{themengebiet}« existiert bereits.\nTrotzdem überschreiben?",
                buttons=[
                    MDFlatButton(text="Nein", on_release=lambda x: dialog.dismiss()),
                    MDRaisedButton(text="Ja", on_release=lambda x: self._override_card(card, dialog))
                ]
            )
            dialog.open()
            return

        if storage.add_card(card):
            self.show_message("Erfolg", f"Karte {karten_nummer_int} in »{themengebiet}« gespeichert!", "success")
            Gamification().log_action("add_card")
            Gamification().check_badges()
            self.clear_fields()
            self._after_enter(0)
        else:
            self.show_message("Fehler", "Speichern fehlgeschlagen.", "error")

    def _override_card(self, card, dialog):
        storage = CardStorage()
        storage.update_card(card)
        self.show_message("Erfolg", "Karte wurde überschrieben!", "success")
        dialog.dismiss()
        self.clear_fields()
        self._after_enter(0)
        
    def correct_text(self, text):
        if not text:
            return ""
        return text

    # -------------------------
    # Checkbox Toggle
    # -------------------------
    def toggle_checkbox(self, option):
        if option == "table":
            active = self.ids.checkbox_table.active
            self.ids.table_grid.opacity = 1 if active else 0
            self.ids.table_grid.disabled = not active
            if active and not hasattr(self, "table_header_names"):
                self.open_table_config_dialog()
        elif option == "image":
            active = self.ids.checkbox_image.active
            self.ids.image_container.opacity = 1 if active else 0
            self.ids.image_container.disabled = not active

    # -------------------------
    # Table Config
    # -------------------------
    def open_table_config_dialog(self):
        if self.table_config_dialog:
            self.table_config_dialog.dismiss()

        layout = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        layout.add_widget(MDLabel(text="Tabellen konfigurieren", bold=True, size_hint_y=None, height=dp(30)))

        self.spalten_input = MDTextField(hint_text="Anzahl Spalten (1–10)", input_filter="int", size_hint_y=None, height=dp(40))
        layout.add_widget(self.spalten_input)

        self.header_container = MDBoxLayout(orientation="vertical", spacing=dp(8))
        layout.add_widget(self.header_container)

        def create_headers(instance):
            self.header_container.clear_widgets()
            try:
                n = int(self.spalten_input.text or "0")
                if not 1 <= n <= 10:
                    raise ValueError
            except ValueError:
                self.show_message("Fehler", "1–10 Spalten erlaubt.", "error")
                return
            self.table_headers = []
            for i in range(n):
                tf = MDTextField(hint_text=f"Spalte {i+1}", size_hint_y=None, height=dp(40))
                self.header_container.add_widget(tf)
                self.table_headers.append(tf)

        btn_create = MDRaisedButton(text="Header erstellen", size_hint_y=None, height=dp(40))
        btn_create.bind(on_release=create_headers)
        layout.add_widget(btn_create)

        def finalize_table(instance):
            headers = [tf.text.strip() for tf in self.table_headers]
            if not any(headers):
                self.show_message("Fehler", "Mindestens ein Header nötig.", "error")
                return
            self.table_header_names = headers
            self.ids.table_grid.clear_widgets()
            for h in headers:
                self.ids.table_grid.add_widget(MDLabel(
                    text=h, bold=True, halign="center",
                    size_hint_y=None, height=dp(40),
                    theme_text_color="Primary"
                ))
            if self.table_config_dialog:
                self.table_config_dialog.dismiss()

        btn_finalize = MDRaisedButton(text="Tabelle aktivieren", size_hint_y=None, height=dp(40))
        btn_finalize.bind(on_release=finalize_table)
        layout.add_widget(btn_finalize)

        self.table_config_dialog = MDDialog(type="custom", content_cls=layout, auto_dismiss=False)
        self.table_config_dialog.open()

    def add_table_row(self):
        if not hasattr(self, "table_header_names"):
            return
        for _ in self.table_header_names:
            self.ids.table_grid.add_widget(MDTextField(
                hint_text="Eintrag...", size_hint_y=None, height=dp(40)
            ))

    def remove_table_row(self):
        if not hasattr(self, "table_header_names"):
            return
        for _ in self.table_header_names:
            if self.ids.table_grid.children and isinstance(self.ids.table_grid.children[0], MDTextField):
                self.ids.table_grid.remove_widget(self.ids.table_grid.children[0])
                
    # -------------------------
    # Image: File + Camera 
    # -------------------------
    def open_file_chooser(self):
        if self.filechooser_dialog:
            self.filechooser_dialog.dismiss()
            self.filechooser_dialog = None  # Reset

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        filechooser = FileChooserListView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.bmp"],
            path=os.path.expanduser("~")
        )
        content.add_widget(filechooser)

        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        # OK-Button
        ok_btn = MDRaisedButton(text="Auswählen", on_release=lambda x: self._file_selected(filechooser.selection))
        btn_box.add_widget(ok_btn)

        # Abbrechen-Button – NACH Dialog-Erstellung!
        def cancel_action(x):
            if self.filechooser_dialog:
                self.filechooser_dialog.dismiss()

        cancel_btn = MDFlatButton(text="Abbrechen", on_release=cancel_action)
        btn_box.add_widget(cancel_btn)

        content.add_widget(btn_box)

        # Erst jetzt: Dialog erstellen
        self.filechooser_dialog = MDDialog(type="custom", content_cls=content, auto_dismiss=False)
        self.filechooser_dialog.open()


    def _file_selected(self, selection):
        if not selection:
            self.show_message("Info", "Keine Datei gewählt.", "warning")
            return
        sel = selection[0]
        try:
            with open(sel, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            ext = os.path.splitext(sel)[1].lower().lstrip(".")
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
            self.selected_image_data_uri = f"data:{mime};base64,{b64}"
            self.ids.image_preview_label.text = f"Bild: {os.path.basename(sel)}"
            if self.filechooser_dialog:
                self.filechooser_dialog.dismiss()
                self.filechooser_dialog = None  # Sauber
        except Exception as e:
            self.show_message("Fehler", f"Bildfehler: {e}", "error")


    def open_camera_dialog(self):
        if self.camera_dialog:
            self.camera_dialog.dismiss()
            self.camera_dialog = None

        layout = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        cam = None
        try:
            # Kamera nur versuchen – bei Fehler abfangen
            cam = Camera(play=False, index=0, resolution=(640, 480), size_hint_y=None, height=dp(320))
            layout.add_widget(cam)
            Clock.schedule_once(lambda dt: cam and setattr(cam, 'play', True), 0.5)
        except Exception as e:
            print(f"[Kamera] Nicht verfügbar: {e}")
            self.show_message("Kamera nicht verfügbar", "Bitte nutze Datei-Upload.", "warning")
            return  # Abbruch – kein Dialog

        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        capture_btn = MDRaisedButton(text="Foto machen", on_release=lambda x: self._capture_camera(cam))
        btn_box.add_widget(capture_btn)

        def close_action(x):
            if self.camera_dialog:
                self.camera_dialog.dismiss()

        close_btn = MDFlatButton(text="Schließen", on_release=close_action)
        btn_box.add_widget(close_btn)

        layout.add_widget(btn_box)

        # Erst jetzt: Dialog erstellen
        self.camera_dialog = MDDialog(type="custom", content_cls=layout, auto_dismiss=False)
        self.camera_dialog.open()


    def _capture_camera(self, cam: Camera):
        if not cam:
            return
        try:
            fd, tmp = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            cam.export_to_png(tmp)
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            b64 = base64.b64encode(data).decode("utf-8")
            self.selected_image_data_uri = f"data:image/png;base64,{b64}"
            self.ids.image_preview_label.text = "Foto aufgenommen"
            if self.camera_dialog:
                self.camera_dialog.dismiss()
                self.camera_dialog = None
        except Exception as e:
            self.show_message("Fehler", f"Kamerafehler: {e}", "error")

    # -------------------------
    # Category Chips
    # -------------------------
    def set_category(self, category):
        self.selected_category = category
        active = (0.0, 0.6, 0.0, 1)
        inactive = (0.0, 0.447, 0.6, 1)
        chip_map = {
            "AP1": "ap1_chip",
            "AP2": "ap2_chip",
            "WISO": "wiso_chip",
            "Sonstiges": "else_chip"
        }
        for cat, chip_id in chip_map.items():
            chip = self.ids.get(chip_id)
            if chip:
                chip.md_bg_color = active if cat == category else inactive

    # -------------------------
    # Clear
    # -------------------------
    def clear_fields(self):
        for field in ["themengebiet", "karten_nummer", "frage", "antwort_kurz", "antwort_detail"]:
            if field in self.ids:
                self.ids[field].text = ""
        self.ids.checkbox_table.active = False
        self.ids.checkbox_image.active = False
        self.selected_image_data_uri = None
        self.ids.image_preview_label.text = "Kein Bild ausgewählt"
        self.ids.table_grid.clear_widgets()
        self.table_header_names = []
        if hasattr(self, "table_headers"):
            del self.table_headers