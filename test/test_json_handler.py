# test_json_handler.py
import pytest
from utils.json_handler import CardStorage
import os

@pytest.fixture
def storage():
    test_file = "data/test_cards.jsonl"
    storage = CardStorage()
    yield storage
    if os.path.exists(test_file):
        os.remove(test_file)

def test_add_card(storage):
    card = {
        "karten_nummer": 99,
        "theme": "Test",
        "question": "Was ist Test?",
        "answer": {"simple": "Test", "detailed": "Test"},
    }
    assert storage.add_card(card)
    cards = storage.load_cards()
    assert len(cards) == 1
    assert cards[0]["karten_nummer"] == 99

def test_delete_card(storage):
    card = {"karten_nummer": 99, "theme": "Test", "question": "Test", "answer": {"simple": "Test", "detailed": "Test"}}
    storage.add_card(card)
    assert storage.delete_card(99)
    assert len(storage.load_cards()) == 0