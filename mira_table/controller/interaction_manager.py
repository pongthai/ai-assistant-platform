from mira_table.state_machine.state_manager import StateManager, State
from mira_table.api.server_api import send_text_to_server, reset_session, play_tts
from core.audio.voice_listener import VoiceListener
from core.audio.audio_controller import AudioController
from mira_table.config import SESSION_ID
import core.audio.audio_config

import time
import threading
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

class PlaybackHandler:
    def on_audio_start(self):
        print("[Handler] 🔊 Audio playback started")

    def on_audio_stop(self):
        print("[Handler] 🔇 Audio playback stopped")

class InteractionManager:
    def __init__(self, session_id=SESSION_ID):
        logger.debug("InteractionManager - Initialzied")
        self.session_id = session_id
        self.state = StateManager()
        #self.voice_listener = VADVoiceListener()
        wake_event = threading.Event()
        playback_handler = PlaybackHandler()
        self.audio_controller = AudioController(playback_handler=playback_handler )       
        self.voice_listener = VoiceListener(self.audio_controller,wake_event,stt_vendor="google_cloud")
        self.voice_listener.pause_background_listener()               

    def run(self):
        self.state.set_state(State.START)

        while True:
            current_state = self.state.get_state()

            if current_state == State.START:
                logger.debug("🔄 Resetting session and greeting user...")
                reset_session(self.session_id)
                self.state.set_state(State.GREETING)

            elif current_state == State.GREETING:
                response = send_text_to_server("สวัสดี", self.session_id)
                self.handle_response(response)

            elif current_state == State.LISTENING:
                logger.info("🎧 Listening for user input...")
                user_text = self.voice_listener.listen()
                logger.info(f"user_text={user_text}")
                if user_text:
                    response = send_text_to_server(user_text, self.session_id)
                    self.handle_response(response)
                else:
                    logger.info("🤷 ไม่เข้าใจเสียงที่พูด ลองใหม่อีกครั้ง")

            elif current_state == State.CONFIRMING:
                logger.info("📋 สรุปออเดอร์และยืนยัน")
                user_text = self.voice_listener.listen()
                if user_text:
                    response = send_text_to_server(user_text, self.session_id)
                    self.handle_response(response)
                else:
                    logger.warning("❌ ไม่เข้าใจคำพูดในการยืนยัน")
                    self.state.set_state(State.LISTENING)  # หรือวนกลับให้ฟังใหม่

            elif current_state == State.THANK_YOU:
                logger.info("🙏 ขอบคุณลูกค้า")
                time.sleep(2)
                self.state.set_state(State.END)

            elif current_state == State.END:
                logger.info("🔁 กลับสู่การเริ่มต้นใหม่")
                self.state.set_state(State.START)

    def handle_response(self, response_json):
        if response_json is None:
            logger.error("❌ ไม่สามารถเชื่อมต่อกับ server หรือ server ไม่ตอบกลับ")
            self.state.set_state(State.LISTENING)
            return

        logger.info(f"response_json={response_json}")
        intent = response_json.get("intent")
        tts_url = response_json.get("tts_url")

        if tts_url:
            play_tts(tts_url)

        if intent == "greeting":
            self.state.set_state(State.LISTENING)

        elif intent == "add_order":
            self.state.set_state(State.LISTENING)
        
        elif intent == "cancel_order":
            self.state.set_state(State.LISTENING)

        elif intent == "modify_order":
            self.state.set_state(State.LISTENING)

        elif intent == "show_menu":
            self.state.set_state(State.LISTENING)
        
        elif intent == "show_promotion":
            self.state.set_state(State.LISTENING)

        elif intent == "request_bill":
            self.state.set_state(State.LISTENING)

        elif intent == "confirm_order":
            self.state.set_state(State.CONFIRMING)
            
        elif intent == "payment_method":
            self.state.set_state(State.LISTENING)

        elif intent == "open_topic":
            self.state.set_state(State.LISTENING)
    
        elif intent == "recommend_dish":
            self.state.set_state(State.LISTENING)

        elif intent == "thank_you":
            self.state.set_state(State.THANK_YOU)

        else:
            logger.warning(f"⚠️ ไม่รู้จัก intent: {intent}, default to LISTENING")
            self.state.set_state(State.LISTENING)