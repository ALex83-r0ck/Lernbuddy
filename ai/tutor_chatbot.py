# ai/tutor_chatbot.py
import ollama

class ChatbotTutor:
    def __init__(self):
        self.history = []

    def ask(self, question):
        # Einfacher Prompt
        prompt = f"""
Du bist ein freundlicher Lern-Tutor für WISO.
Antworte kurz und klar.

Frage: {question}
Antwort:
"""

        try:
            response = ollama.generate(model="llama3.1:8b", prompt=prompt)
            answer = response['response'].strip()
        except Exception as e:
            answer = f"Fehler: {e}"

        self.history.append({"user": question, "bot": answer})
        return answer