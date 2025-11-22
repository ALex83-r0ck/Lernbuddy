# lernbuddy/services/quiz_service.py
from typing import List, Optional, Dict
import random
from utils.json_handler import CardStorage
from datetime import datetime


class QuizService:
    """Business-Logik für Quiz: Fragenpool, Auswahl, Bewertung (difficulty/streak)."""

    def __init__(self, storage: Optional[CardStorage] = None):
        self.storage = storage or CardStorage()
        self.pool: List[Dict] = []
        self.active_questions: List[Dict] = []
        self.current_index = 0

    def load_pool(self) -> List[Dict]:
        self.pool = self.storage.load_cards()
        return self.pool

    def filter_by_themes(self, themes: List[str]) -> List[Dict]:
        return [c for c in self.pool if c.get("lernfeld") in themes]

    def prepare_quiz(self, themes: List[str], num_questions: int, randomize: bool = True) -> List[Dict]:
        cards = self.filter_by_themes(themes)
        if randomize:
            random.shuffle(cards)
        self.active_questions = cards[: max(0, int(num_questions))]
        self.current_index = 0
        return self.active_questions

    def get_current_question(self) -> Optional[Dict]:
        if self.current_index < len(self.active_questions):
            return self.active_questions[self.current_index]
        return None

    def answer_current(self, user_answer: str, evaluate_fn) -> Dict:
        """
        evaluate_fn(card, user_answer) -> bool
        Wird in UI/Controller gestellt (z.B. Ollama-Check). Hier nur Update-Logik.
        """
        card = self.get_current_question()
        if not card:
            raise RuntimeError("Keine aktive Frage")

        correct = bool(evaluate_fn(card, user_answer))

        # Update local card fields
        if correct:
            card["correct_streak"] = card.get("correct_streak", 0) + 1
            if card["correct_streak"] >= 3:
                card["difficulty"] = "grün"
            elif card["correct_streak"] >= 1:
                card["difficulty"] = "gelb"
        else:
            card["correct_streak"] = 0
            card["difficulty"] = "rot"

        card["last_reviewed"] = datetime.now().isoformat()

        # Persist only changed fields to avoid accidental overwrites
        try:
            self.storage.update_card_partial(card)
        except Exception:
            # Fail silently; higher layers können das loggen
            pass

        # advance pointer
        self.current_index += 1
        return {"card": card, "correct": correct}
