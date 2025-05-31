import os
import time
import threading
from datetime import datetime, timedelta
from server.config.config import TTS_PATH
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

def cleanup_old_tts_files(ttl_minutes=15, interval_seconds=300):
    def task():
        while True:
            now = datetime.now()
            threshold = now - timedelta(minutes=ttl_minutes)

            for filename in os.listdir(TTS_PATH):
                path = os.path.join(TTS_PATH, filename)
                if os.path.isfile(path) and path.endswith(".mp3"):
                    try:
                        created_time = datetime.fromtimestamp(os.path.getctime(path))
                        if created_time < threshold:
                            os.remove(path)
                            logger.info(f"🧹 Removed old TTS file: {filename}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to delete {filename}: {e}")

            time.sleep(interval_seconds)

    threading.Thread(target=task, daemon=True).start()