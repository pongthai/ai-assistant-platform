import speech_recognition as sr
from utils.logger import get_logger

logger = get_logger(__name__)
recognizer = sr.Recognizer()


def listen_and_recognize(timeout=5, phrase_time_limit=10):
    try:
        with sr.Microphone() as source:
            logger.info("🎧 Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio, language="th-TH")
            return text.strip()

    except sr.WaitTimeoutError:
        logger.warning("⏱️ Listening timed out")
    except sr.UnknownValueError:
        logger.warning("🤷 ไม่เข้าใจเสียงที่พูด")
    except sr.RequestError as e:
        logger.error(f"❌ Speech Recognition service error: {e}")
    except Exception as e:
        logger.error(f"⚠️ Unknown error during recognition: {e}")

    return ""