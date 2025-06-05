from mira_table.state_machine.state_manager import StateManager, State
from mira_table.api.server_api import send_text_to_server, reset_session, play_tts
from core.audio.voice_listener import VoiceListener
from core.audio.audio_controller import AudioController
from mira_table.config import SESSION_ID
from core.audio.processing_sound import ProcessingSound
import core.audio.audio_config

import time
import threading
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

class PlaybackHandler:
    def __init__(self, on_avatar_talk=None):
        self.on_avatar_talk = on_avatar_talk

    def on_audio_start(self):
        print("[Handler] 🔊 Audio playback started")
        if self.on_avatar_talk:
            self.on_avatar_talk(True)

    def on_audio_stop(self):
        print("[Handler] 🔇 Audio playback stopped")
        if self.on_avatar_talk:
            self.on_avatar_talk(False)

class InteractionManager:
    def __init__(self, session_id=SESSION_ID, result_callback=None, on_avatar_talk=None):
        logger.debug("InteractionManager - Initialzied")
        self.session_id = session_id
        self.state = StateManager()
        #self.voice_listener = VADVoiceListener()
        wake_event = threading.Event()
        playback_handler = PlaybackHandler(on_avatar_talk=on_avatar_talk)
        self.audio_controller = AudioController(playback_handler=playback_handler)
        self.processing_sound = ProcessingSound(self.audio_controller)
        self.voice_listener = VoiceListener(self.audio_controller, wake_event, stt_vendor="google_cloud")
        self.voice_listener.pause_background_listener()
        self.result_callback = result_callback
        self.voice_listener.last_user_text = ""

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
                if user_text :
                    self.voice_listener.last_user_text = user_text
                    self.processing_sound.start()
                    response = send_text_to_server(user_text, self.session_id)
                    self.processing_sound.stop()
                    self.handle_response(response)
                # else:
                #     logger.info("🤷 ไม่เข้าใจเสียงที่พูด ลองใหม่อีกครั้ง")

            elif current_state == State.CONFIRMING:
                logger.info("📋 สรุปออเดอร์และยืนยัน")
                user_text = self.voice_listener.listen()
                if user_text:
                    self.voice_listener.last_user_text = user_text
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
        response_ssml = response_json.get("response_ssml")
        intent = response_json.get("intent")
        logger.info(f"intent = {intent}")
        logger.info(f"response_ssml = {response_ssml}")

        if self.result_callback:
            try:
                callback_data = {
                    "user_text": getattr(self.voice_listener, "last_user_text", None),
                    "response_ssml": response_ssml,
                }
                orders = response_json.get("orders")
                total_price = response_json.get("total_price")
                discount = response_json.get("discount")
                if isinstance(orders, list):
                    callback_data["orders"] = orders
                callback_data["total_price"] = total_price
                callback_data["discount"] = discount
                
                self.result_callback(callback_data)
            except Exception as e:
                logger.error(f"❌ result_callback error: {e}")
        
        if response_ssml:
            self.audio_controller.speak(response_ssml,is_ssml=True)

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
            self.state.set_state(State.LISTENING)
            
        elif intent == "payment_method":
            self.state.set_state(State.LISTENING)

        elif intent == "open_topic":
            self.state.set_state(State.LISTENING)
    
        elif intent == "recommend_dish":
            self.state.set_state(State.LISTENING)
        elif intent == "proactive_suggestion":
            self.state.set_state(State.LISTENING)

        elif intent == "thank_you":
            self.state.set_state(State.THANK_YOU)

        else:
            logger.warning(f"⚠️ ไม่รู้จัก intent: {intent}, default to LISTENING")
            self.state.set_state(State.LISTENING)