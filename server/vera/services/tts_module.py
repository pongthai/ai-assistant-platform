from google.cloud import texttospeech
from server.config.config import TTS_PROVIDER
from core.utils.logger_config import get_logger
import os

logger = get_logger(__name__)

def generate_tts(text: str, output_path: str):
    if TTS_PROVIDER == "GoogleCloudTTS":

        client = texttospeech.TextToSpeechClient()

        # ตรวจว่าเป็น SSML หรือไม่
        if text.strip().startswith("<speak>"):
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
            logger.info("🔤 Using SSML input")
        else:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            logger.info("🔤 Using plain text input")

        voice = texttospeech.VoiceSelectionParams(
            language_code="th-TH",
            name="th-TH-Standard-A"  # ✅ ปลอดภัย ใช้ได้ทั่วไป
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        logger.info(f"🔊 TTS audio saved to: {output_path}")

    else:
        raise NotImplementedError(f"TTS provider '{TTS_PROVIDER}' is not supported.")
    