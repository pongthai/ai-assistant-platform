import time
from core.audio.tts_manager import TTSManager
from core.audio.audio_controller import AudioController

# Pre-defined text to test TTS
test_text = "สวัสดีครับ ยินดีต้อนรับเข้าสู่ระบบผู้ช่วยอัจฉริยะของคุณ"

class TestPlaybackHandler:
    def on_audio_start(self):
        print("[Handler] 🔊 Audio playback started")

    def on_audio_stop(self):
        print("[Handler] 🔇 Audio playback stopped")

def test_tts_playback():
    print("🟢 Initializing TTS Manager and Audio Controller...")
    tts_manager = TTSManager()
    playback_handler = TestPlaybackHandler()

    audio_controller = AudioController(playback_handler=playback_handler)

    print("🔊 Generating audio from TTS...")
    audio_path = tts_manager.synthesize(test_text)
    print(f"audio_path: {audio_path}")

    if audio_path:
        print(f"✅ Audio file generated: {audio_path}")
        print("▶️ Playing back the audio...")
        audio_controller.play_audio(audio_path)

        # Wait for playback to finish
        print(f"audio_controller.is_sound_playing: {audio_controller.is_sound_playing}")
        audio_controller.stop_flag.wait()
        #while audio_controller.is_sound_playing:
        #    time.sleep(0.5)
        print("✅ Playback complete.")
    else:
        print("❌ Failed to generate audio.")

if __name__ == "__main__":
    test_tts_playback()