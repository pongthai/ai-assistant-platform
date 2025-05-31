import threading
import time
from core.audio.voice_listener import VoiceListener
from core.config.config import WAKE_WORDS
import core.audio.audio_config

class DummyAudioController:
    @property
    def is_sound_playing(self):
        return False

def test_voice_listener():
    wake_event = threading.Event()
    audio_controller = DummyAudioController()
    listener = VoiceListener(audio_controller, wake_event, stt_vendor="google_cloud")

    print("🟡 Say the wake word to begin (e.g., one of: ", WAKE_WORDS, ")")
    while True:
        listener.wake_word_event.clear()
        print("🎧 Waiting for wake word...")
        listener.wake_word_event.wait()
        print("✅ Wake word detected")
        listener.pause_background_listener()        

        last_active_time = time.time()
        while True:
            print("🎤 Listening for normal speech...")
            full_text = listener.listen()
            if full_text:
                print("🗣️ Recognized speech:", full_text)
                last_active_time = time.time()
            else:
                print("😶 Could not recognize speech")

            if time.time() - last_active_time > 60:
                print("⏳ Idle timeout. Returning to wake word detection...")
                listener.resume_background_listener()                
                break


if __name__ == "__main__":
    test_voice_listener()