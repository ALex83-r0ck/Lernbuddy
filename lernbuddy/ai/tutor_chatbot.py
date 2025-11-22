# ai/tutor_chatbot.py
import threading
from kivy.clock import Clock
import random
import logging

# Logging aktivieren (hilfreich für Fehlersuche)
logging.basicConfig(level=logging.INFO, format="[TutorBot] %(message)s")

# 💬 Offline-Antworten – humorvoll & motivierend
OFFLINE_RESPONSES = [
    "Stell dir vor, du bist ein Azubi-Superheld! Deine Superkraft: WISO verstehen! Du schaffst das!",
    "Tipp: Lies die Frage zweimal – dann kommt der Geistesblitz von ganz allein!",
    "Merksatz: Wer übt, der siegt. Und du bist grad mitten im Sieg!",
    "Pro-Tipp: Kurz aufstehen, dehnen, Kaffee schnappen – und dann rockst du das!",
    "Jede falsche Antwort ist ein Sprungbrett zum Verstehen. Weiter so!",
    "HGB? Kein Problem! Denk an 'Hab Gut Buch' – und du hast’s gut gebucht!",
    "Recht? Einfach merken: Was du nicht willst, dass man dir tu, das füg auch keinem andern zu!",
    "AP2 ist nur AP1 mit Bart. Und du hast AP1 fast im Sack!",
    "Du bist nicht langsam – du bist gründlich. Und gründlich gewinnt immer!",
    "Heute Azubi, morgen Chef. Und Chefs kennen sich aus!",
]

# 🧠 Ollama optional importieren
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class ChatbotTutor:
    """
    Ein freundlicher Lern-Tutor mit optionaler Ollama-Unterstützung.
    Offline fallbacked er auf motivierende Standardantworten.
    """

    def __init__(self):
        self.history = []
        self.use_ollama = OLLAMA_AVAILABLE

        if self.use_ollama:
            logging.info("Ollama erkannt ✅ – Tutor läuft im KI-Modus.")
        else:
            logging.info("Ollama nicht gefunden ⚠️ – Offline-Modus aktiviert.")

    # -------------------------------------------------------
    # Öffentliche API
    # -------------------------------------------------------
    def ask(self, question: str, callback):
        """
        Fragt den Tutor etwas. Antwort wird asynchron an 'callback' geschickt.
        :param question: Eingabe des Users
        :param callback: Funktion, die Antwort verarbeitet (UI-seitig)
        """
        if not question.strip():
            Clock.schedule_once(lambda dt: callback("Frag mich irgendwas 😄"))
            return

        def run():
            # 🧩 Ollama verwenden, wenn möglich
            if self.use_ollama:
                try:
                    prompt = (
                        "Du bist ein super motivierender Lern-Tutor für Azubis.\n"
                        "Antworte kurz, klar, freundlich, manchmal mit einem Merksatz oder kleinen Eselsbrücken.\n"
                        f"Frage: {question.strip()}\n"
                        "Antwort:"
                    )
                    response = ollama.generate(
                        model="gemma2:2b",
                        prompt=prompt,
                        options={"temperature": 0.8, "num_predict": 200, "timeout": 10},
                    )
                    answer = response.get("response", "").strip()
                    if not answer:
                        raise ValueError("Leere Ollama-Antwort erhalten.")
                except Exception as e:
                    logging.error(f"Ollama-Fehler: {e}")
                    answer = (
                        random.choice(OFFLINE_RESPONSES)
                        + "\n\n(Ollama offline – aber ich bleib motiviert 💪)"
                    )
            else:
                # 📴 Offline fallback
                answer = random.choice(OFFLINE_RESPONSES) + "\n\n(Offline-Modus aktiv 🧠)"

            # Verlauf speichern (max 20 Einträge)
            self.history.append({"frage": question, "antwort": answer})
            if len(self.history) > 20:
                self.history.pop(0)

            # Antwort zurück in den Hauptthread (Kivy)
            Clock.schedule_once(lambda dt: callback(answer))

        # 🔄 Hintergrundthread starten
        threading.Thread(target=run, daemon=True).start()

    # -------------------------------------------------------
    # Extra: Verlauf abrufen oder löschen
    # -------------------------------------------------------
    def get_history(self):
        """Gibt bisherigen Chat-Verlauf zurück."""
        return list(self.history)

    def clear_history(self):
        """Setzt den Chat-Verlauf zurück."""
        self.history.clear()
