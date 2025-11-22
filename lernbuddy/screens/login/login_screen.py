from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
import re
import sqlite3
import bcrypt

DB_FILE = "database/users.db"

class LoginScreen(MDScreen):
    def on_pre_enter(self):
        self.setup_db()

    def login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if not username or not password:
            self.show_dialog("Fehler", "Username und Password eingeben.")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = c.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if app:
                app.switch_screen("splash")
        else:
            self.show_dialog("Fehler", "Falsche Credentials.")

    def validate_password(self, password):
        if (len(password)< 8 or 
            not re.search("[A-Z]", password) or
            not re.search("[a-z]", password) or
            not re.search("[0-9]", password) or
            not re.search("[!@#$%^&*()]", password)):
            return False
        return True

    def register(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if not username or not password:
            self.show_dialog("Fehler", "Username und Password eingeben.")
            return
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*]", password):
            self.show_dialog("Fehler", "Passwort: min. 8 Zeichen, 1 Großbuchstabe, 1 Zahl, 1 Sonderzeichen.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed.decode()))
            conn.commit()
            self.show_dialog("Erfolg", "User registriert – jetzt login.")
        except sqlite3.IntegrityError:
            self.show_dialog("Fehler", "Username existiert bereits.")
        conn.close()

    # Admin bei erstem Start
    def setup_db(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            admin_hash = bcrypt.hashpw("Admin123!".encode(), bcrypt.gensalt()).decode()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", admin_hash))
        conn.commit()
        conn.close()

    def show_dialog(self, title, message):
        MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        ).open()

   