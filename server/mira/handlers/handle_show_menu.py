

from server.mira.services.menu import MENU_DATA
from server.mira.models.response import create_response

def handle_show_menu(session_id: str, params: dict) -> dict:
    menu_names = [item["name"] for item in MENU_DATA]
    menu_text = " ".join(menu_names)
    response_text = f"<speak><prosody rate='108%' pitch='+1st'>เมนูของเราวันนี้ได้แก่ <break time='300ms'/> {menu_text}</prosody></speak>"
    return create_response(intent="show_menu", response=response_text)