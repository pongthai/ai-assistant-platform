import json
import unicodedata
import os
import re
from typing import Optional, List

# Load menu data
MENU_FILE_PATH = os.path.join(os.path.dirname(__file__), "../data/menu.json")

with open(MENU_FILE_PATH, "r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text.strip().lower())


def lookup_price(item_name: str) -> Optional[float]:
    norm_input = normalize_text(item_name)
    for item in MENU_DATA:
        if normalize_text(item["name"]) == norm_input or norm_input in normalize_text(item["name"]):
            return item["price"]
    return None


def validate_item(item_name: str) -> bool:
    norm_input = normalize_text(item_name)
    for item in MENU_DATA:
        norm_menu_name = normalize_text(item["name"])
        if norm_input == norm_menu_name:
            return True
        if norm_input in norm_menu_name:
            return True
        if re.search(rf"^{re.escape(norm_input)}", norm_menu_name):
            return True
    return False


def get_recommended_items() -> List[dict]:
    return [item for item in MENU_DATA if item.get("recommended", False)]


def suggest_complementary_items(current_items: List[str]) -> List[str]:
    suggestions = []
    for item in MENU_DATA:
        if "pair_with" in item:
            for current in current_items:
                if normalize_text(current) in [normalize_text(pair) for pair in item["pair_with"]]:
                    suggestions.append(item["name"])
    return list(set(suggestions))
