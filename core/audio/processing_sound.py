# core/audio/processing_sound.py (หรือ path ที่คุณวางไว้)

import threading
import time
import sounddevice as sd
import soundfile as sf
from core.utils.logger_config import get_logger
from core.config.config import PROCESSING_SOUND_FILE

logger = get_logger(__name__)

class ProcessingSound:
    def __init__(self, audio_controller, filepath=PROCESSING_SOUND_FILE):
        self.audio_controller = audio_controller
        self.filepath = filepath
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return  # already playing

        def _loop():
            try:
                data, samplerate = sf.read(self.filepath, dtype='float32')
                channels = data.shape[1] if len(data.shape) > 1 else 1

                self.audio_controller.is_playing = True
                self._stop_event.clear()

                with sd.OutputStream(samplerate=samplerate, channels=channels) as stream:
                    while not self._stop_event.is_set():
                        i = 0
                        while i < len(data):
                            if self._stop_event.is_set():
                                break
                            stream.write(data[i:i+1024])
                            i += 1024
                        time.sleep(1)
            except Exception as e:
                logger.error(f"❌ Error playing processing sound: {e}")
            finally:
                self.audio_controller.is_playing = False

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()