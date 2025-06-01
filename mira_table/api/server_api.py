import requests
import tempfile
import os
import pygame
from mira_table.config import SERVER_HOST
from core.utils.logger_config import get_logger

logger = get_logger(__name__)


def send_text_to_server(text, session_id="default-session"):
    try:
        response = requests.post(
            f"{SERVER_HOST}/ask",
            json={"user_input": text, "session_id": session_id}
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Server responded with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error connecting to server: {e}")
        return None


def play_tts(tts_url):
    try:
        url = f"{SERVER_HOST}{tts_url}"
        res = requests.get(url)
        if res.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(res.content)
                tmp.flush()
                pygame.mixer.init()
                pygame.mixer.music.load(tmp.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pass
            os.unlink(tmp.name)
        else:
            logger.warning(f"TTS not found: {res.status_code}")
    except Exception as e:
        logger.error(f"Error playing TTS: {e}")


def reset_session(session_id="default-session"):
    try:
        response = requests.post(
            f"{SERVER_HOST}/reset-session",
            json={"session_id": session_id}
        )
        if response.status_code == 200:
            logger.info(f"✅ Session {session_id} reset successfully")
            return True
        else:
            logger.warning(f"❌ Failed to reset session: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        return False