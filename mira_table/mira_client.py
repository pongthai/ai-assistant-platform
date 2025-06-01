import requests
import sounddevice as sd
import soundfile as sf
import io

API_URL = "http://localhost:8000/mira/ask"

def record_voice(duration=4, samplerate=16000):
    print("🎙️ Recording...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("✅ Recording complete.")
    return recording, samplerate

def play_audio(audio_bytes):
    with io.BytesIO(audio_bytes) as f:
        data, samplerate = sf.read(f, dtype='int16')
        sd.play(data, samplerate)
        sd.wait()

def send_text_input(user_input, session_id="default_user"):
    response = requests.post(
        API_URL,
        headers={"X-Session-ID": session_id},
        json={"user_input": user_input}
    )
    response.raise_for_status()
    return response.json()

def main():
    session_id = "table_001"
    print("🧠 MIRA Table Assistant Ready")

    while True:
        user_input = input("\n🗣️ Say something (or type 'exit'): ")
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        try:
            result = send_text_input(user_input, session_id)
            print(f"\n🤖 MIRA: {result.get('reply_text', '')}")

            if "tts_path" in result:
                with open(result["tts_path"], "rb") as f:
                    audio_bytes = f.read()
                    play_audio(audio_bytes)

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
