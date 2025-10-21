# eingabe_screen.py
import os
import base64
import tempfile
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.camera import Camera
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

from utils.json_handler import CardStorage


class EingabeScreen(MDScreen):
    """
    Screen zur Erstellung neuer Lernkarten.
    Unterstützt Texteingaben, Tabellen mit Header-Konfiguration, Bilder (Datei + Kamera) und Kategorien.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.filechooser_dialog = None
        self.camera_dialog = None
        self.table_config_dialog = None
        self.table_data = []
        self.selected_category = None
        self.selected_image_data_uri = None  # enthält data:image/...;base64,...

    # -------------------------
    # lifecycle
    # -------------------------
    def on_pre_enter(self):
        storage = CardStorage()
        count = len(storage.load_cards())
        if hasattr(self.ids, "top_bar"):
            self.ids.top_bar.title = f"Lernkarten erstellen (Gespeicherte Fragen: {count})"

    # -------------------------
    # messages / dialog helpers
    # -------------------------
    def show_message(self, title, message, color="error"):
        if self.dialog:
            self.dialog.dismiss()

        config = {
            "error": {"icon": "alert-circle", "bg_color": [1, 0.95, 0.95, 1], "title_color": [0.8, 0.1, 0.1, 1], "text_color": [0.3, 0.1, 0.1, 1], "button_color": [0.9, 0.2, 0.2, 1]},
            "success": {"icon": "check-circle", "bg_color": [0.95, 1, 0.95, 1], "title_color": [0.1, 0.6, 0.1, 1], "text_color": [0.1, 0.3, 0.1, 1], "button_color": [0.2, 0.7, 0.2, 1]},
            "warning": {"icon": "alert", "bg_color": [1, 0.98, 0.9, 1], "title_color": [0.8, 0.5, 0.1, 1], "text_color": [0.4, 0.2, 0.05, 1], "button_color": [0.95, 0.6, 0.1, 1]},
        }
        cfg = config.get(color, config["error"])

        content = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        header = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(48))
        from kivymd.uix.label import MDIcon
        icon = MDIcon(icon=cfg["icon"], theme_text_color="Custom", text_color=cfg["title_color"], font_size="32sp")
        header.add_widget(icon)
        header.add_widget(MDLabel(text=title, font_style="H6", theme_text_color="Custom", text_color=cfg["title_color"]))
        content.add_widget(header)
        content.add_widget(MDLabel(text=message, theme_text_color="Custom", text_color=cfg["text_color"]))

        dialog = MDDialog(type="custom", content_cls=content, buttons=[MDRaisedButton(text="OK", md_bg_color=cfg["button_color"], on_release=lambda x: dialog.dismiss())])
        self.dialog = dialog
        dialog.open()

    # -------------------------
    # speichern
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

        # Validierungen
        if not themengebiet:
            self.show_message("Fehler", "Bitte geben Sie ein Themengebiet ein.", "error"); return
        if not karten_nummer:
            self.show_message("Fehler", "Bitte geben Sie eine Kartennummer ein.", "error"); return
        if not frage:
            self.show_message("Fehler", "Bitte geben Sie eine Frage ein.", "error"); return

        try:
            karten_nummer_int = int(karten_nummer)
            if karten_nummer_int <= 0:
                raise ValueError
        except ValueError:
            self.show_message("Fehler", "Kartennummer muss eine positive ganze Zahl sein.", "error"); return

        storage = CardStorage()
        if storage.card_number_exists(karten_nummer_int):
            self.show_message("Duplikat", f"Karte mit Nummer {karten_nummer_int} existiert bereits.", "warning"); return

        # Tabelleninhalt sammeln (falls aktiv)
        table = []
        if has_table:
            grid = self.ids.table_grid
            children = list(reversed(grid.children))
            for i in range(0, len(children), len(self.table_headers) if hasattr(self, "table_headers") else 2):
                row = []
                for j in range(len(self.table_headers)):
                    if i+j < len(children):
                        row.append(children[i+j].text.strip())
                if row:
                    table.append(row)

        # Image: falls gesetzt, already stored as data URI
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

        if storage.add_card(card):
            self.show_message("Erfolg", f"Karte {karten_nummer_int} gespeichert.", "success")
            self.clear_fields()
            self.on_pre_enter()
        else:
            self.show_message("Fehler", "Karte konnte nicht gespeichert werden.", "error")

    # -------------------------
    # Tabellen-UI
    # -------------------------
    def toggle_checkbox(self, option):
        if option == "table":
            active = self.ids.checkbox_table.active
            if active:
                self.open_table_config_dialog()
            self.ids.table_grid.opacity = 1 if active else 0
            self.ids.table_grid.disabled = not active
        elif option == "image":
            ic = self.ids.image_container
            active = self.ids.checkbox_image.active
            ic.opacity = 1 if active else 0
            ic.disabled = not active

    def open_table_config_dialog(self):
        """Dialog zur Konfiguration von Spaltenanzahl und Headern."""
        if self.table_config_dialog:
            self.table_config_dialog.dismiss()

        layout = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        layout.add_widget(MDLabel(text="Tabellen konfigurieren", bold=True, size_hint_y=None, height=dp(30)))

        # Spaltenanzahl
        self.spalten_input = MDTextField(hint_text="Anzahl Spalten", input_filter="int", size_hint_y=None, height=dp(40))
        layout.add_widget(self.spalten_input)

        self.header_container = MDBoxLayout(orientation="vertical", spacing=dp(8))
        layout.add_widget(self.header_container)

        def create_headers(instance):
            self.header_container.clear_widgets()
            try:
                n = int(self.spalten_input.text)
                if n <= 0:
                    raise ValueError
            except ValueError:
                self.show_message("Fehler", "Bitte eine gültige positive Zahl eingeben.", "error")
                return
            self.table_headers = []
            for i in range(n):
                tf = MDTextField(hint_text=f"Header {i+1}", size_hint_y=None, height=dp(80))
                self.header_container.add_widget(tf)
                self.table_headers.append(tf)

        btn_create_headers = MDRaisedButton(text="Header Felder erstellen", size_hint_y=None, height=dp(40))
        btn_create_headers.bind(on_release=create_headers)
        layout.add_widget(btn_create_headers)

        def finalize_table(instance):
            headers = [tf.text.strip() for tf in self.table_headers if tf.text.strip()]
            if not headers:
                self.show_message("Fehler", "Bitte mindestens einen Header definieren.", "error")
                return
            self.ids.table_grid.clear_widgets()
            for h in headers:
                self.ids.table_grid.add_widget(MDLabel(text=h, size_hint_y=None, height=dp(40)))
            if self.table_config_dialog:
                self.table_config_dialog.dismiss()

        btn_finalize = MDRaisedButton(text="Tabelle erstellen", size_hint_y=None, height=dp(40))
        btn_finalize.bind(on_release=finalize_table)
        layout.add_widget(btn_finalize)

        self.table_config_dialog = MDDialog(type="custom", content_cls=layout, auto_dismiss=False)
        self.table_config_dialog.open()

    def add_table_row(self):
        if not hasattr(self, "table_headers"):
            return
        for _ in self.table_headers:
            self.ids.table_grid.add_widget(MDTextField(hint_text="...", size_hint_y=None, height=dp(40)))

    def remove_table_row(self):
        if not hasattr(self, "table_headers"):
            return
        for _ in self.table_headers:
            if self.ids.table_grid.children:
                self.ids.table_grid.remove_widget(self.ids.table_grid.children[0])

    # -------------------------
    # image: file chooser + camera
    # -------------------------
    def open_file_chooser(self):
        """Öffnet FileChooser-Dialog."""
        if self.filechooser_dialog:
            self.filechooser_dialog.dismiss()

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        filechooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg", "*.bmp"], path=os.path.expanduser("~"))
        content.add_widget(filechooser)

        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        ok_btn = MDRaisedButton(text="Auswählen", on_release=lambda x: self._file_selected(filechooser.selection))
        cancel_btn = MDFlatButton(text="Abbrechen", on_release=lambda x: self.filechooser_dialog.dismiss() if self.filechooser_dialog else None)
        btn_box.add_widget(ok_btn); btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

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
            ext = os.path.splitext(sel)[1].lower().replace(".", "")
            mime = "image/" + ("jpeg" if ext in ("jpg", "jpeg") else ext or "png")
            self.selected_image_data_uri = f"data:{mime};base64,{b64}"
            self.ids.image_preview_label.text = f"Bild ausgewählt: {os.path.basename(sel)}"
            if self.filechooser_dialog:
                self.filechooser_dialog.dismiss()
        except Exception as e:
            self.show_message("Fehler", f"Bild konnte nicht geladen werden: {e}", "error")

    def open_camera_dialog(self):
        """Öffnet Kamera-Dialog (falls verfügbar)."""
        if self.camera_dialog:
            self.camera_dialog.dismiss()

        layout = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        try:
            cam = Camera(play=True, index=0, resolution=(640, 480), size_hint_y=None, height=dp(320))
            layout.add_widget(cam)
        except Exception:
            self.show_message("Kamera nicht verfügbar", "Bild kann nur aus Datei gewählt werden.", "warning")
            self.selected_image_data_uri = None
            return

        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        capture_btn = MDRaisedButton(text="Capture", on_release=lambda x: self._capture_camera(cam))
        close_btn = MDFlatButton(text="Schließen", on_release=lambda x: self.camera_dialog.dismiss() if self.camera_dialog else None)
        btn_box.add_widget(capture_btn); btn_box.add_widget(close_btn)
        layout.add_widget(btn_box)

        self.camera_dialog = MDDialog(type="custom", content_cls=layout, auto_dismiss=False)
        self.camera_dialog.open()

    def _capture_camera(self, cam: Camera):
        try:
            fd, tmp = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            cam.export_to_png(tmp)
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            b64 = base64.b64encode(data).decode("utf-8")
            self.selected_image_data_uri = f"data:image/png;base64,{b64}"
            self.ids.image_preview_label.text = "Bild aufgenommen (Kamera)"
            if self.camera_dialog:
                self.camera_dialog.dismiss()
        except Exception as e:
            self.show_message("Fehler", f"Beim Erfassen des Bildes ist ein Fehler aufgetreten: {e}", "error")

    # -------------------------
    # category helper
    # -------------------------
    def set_category(self, category):
        self.selected_category = category
        active_color = (0.0, 0.6, 0.0, 1)
        inactive_color = (0.0, 0.447, 0.6, 1)
        for chip_id in ["ap1_chip", "ap2_chip", "wiso_chip", "else_chip"]:
            chip = self.ids.get(chip_id)
            if chip:
                chip.md_bg_color = active_color if chip_id.endswith(category.lower()[:2]) or chip.text.lower() == category.lower() else inactive_color

    # -------------------------
    # clear fields
    # -------------------------
    def clear_fields(self):
        for field in ["themengebiet", "karten_nummer", "frage", "antwort_kurz", "antwort_detail"]:
            try:
                self.ids[field].text = ""
            except Exception:
                pass
        self.ids.checkbox_table.active = False
        self.ids.checkbox_image.active = False
        self.selected_image_data_uri = None
        self.ids.image_preview_label.text = "Kein Bild ausgewählt"
        self.ids.table_grid.clear_widgets()
        self.table_data = []
        if hasattr(self, "table_headers"):
            del self.table_headers
