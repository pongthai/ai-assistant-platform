# mira_client_main.py
from dotenv import load_dotenv
load_dotenv()

import sys
import threading
import requests
import sounddevice as sd
import queue
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTextBrowser
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from google.cloud import speech
from gtts import gTTS
from mira_table.controller.interaction_manager import InteractionManager
import os
from core.utils.logger_config import get_logger

logger = get_logger(__name__)


MIRA_SERVER_URL = os.getenv("MIRA_SERVER_URL")
ORDER_API_URL = os.getenv("ORDER_API_URL")
LANG = os.getenv("GOOGLE_STT_LANG", "th-TH")

# === Voice Input ===
audio_queue = queue.Queue()

class AudioStream:
    def __init__(self):
        self.stream = sd.InputStream(callback=self.callback)

    def callback(self, indata, frames, time, status):
        audio_queue.put(bytes(indata))

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()

class SpeechWorker(QObject):
    update_text = pyqtSignal(str)
    update_result = pyqtSignal(dict)
    update_orders = pyqtSignal(dict)
    set_avatar_talking = pyqtSignal()
    set_avatar_idle = pyqtSignal()
    reply_ready = pyqtSignal(dict)

    def handle_reply_ready(self, data: dict):
        logger.info(f"Enter handle_reply_ready = data={data}")
        self.reply_ready.emit(data)
        if "orders" in data:
            self.update_orders.emit({
                "orders": data.get("orders", []),
                "total_price": data.get("total_price"),
                "discount": data.get("discount")
            })

    def handle_avatar_talk(self, is_talking: bool):
        if is_talking:
            self.set_avatar_talking.emit()
        else:
            self.set_avatar_idle.emit()

    def __init__(self):
        super().__init__()
        self.interaction_manager = InteractionManager(
            result_callback=self.handle_reply_ready,
            on_avatar_talk=self.handle_avatar_talk
        )    

    def run(self):
        def background_run():
            try:
                self.interaction_manager.run()
            except Exception as e:
                print("InteractionManager error:", e)

        thread = threading.Thread(target=background_run, daemon=True)
        thread.start()

# === UI ===
class MiraUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.avatar_scale = 0.60  # Default scale factor for avatar
        self.setWindowTitle("MIRA Client")
        #self.setGeometry(50, 50, 1024, 600)
        self.setGeometry(10, 10, 1200, 400)

        self.order_list = QListWidget()
        self.avatar_label = QLabel()
        self.avatar_movie = QMovie("./mira_client_pi/assets/pingping_static_v3.png")
        if not self.avatar_movie.isValid():
            print("❌ QMovie failed to load GIF")
        # self.avatar_movie.setScaledSize(
        #     self.avatar_movie.currentPixmap().size() * self.avatar_scale
        # )
        self.avatar_label.setMovie(self.avatar_movie)
        self.avatar_movie.start()

        self.menu_info = QTextBrowser()
        self.menu_info.setText("Waiting for command...")

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.avatar_label)
        right_panel.addWidget(self.menu_info)

        layout = QHBoxLayout()
        layout.addWidget(self.order_list, 2)
        layout.addLayout(right_panel, 3)

        self.setLayout(layout)

        self.thread = QThread()
        self.worker = SpeechWorker()
        self.worker.moveToThread(self.thread)

        self.worker.update_text.connect(self.menu_info.setText)
        self.worker.update_result.connect(lambda res: self.update_menu_info(res['menu_name'], res['description']))
        self.worker.update_orders.connect(self.update_order_list)
        self.worker.set_avatar_talking.connect(self.play_avatar_talking)
        self.worker.set_avatar_idle.connect(self.play_avatar_idle)
        self.worker.reply_ready.connect(self.handle_reply_ready)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def update_order_list(self, order_data):
        self.order_list.clear()
        logger.info("Enter update_order_list")
        if isinstance(order_data, list):
            orders = order_data
            total_price = None
            discount = None
        else:
            orders = order_data.get("orders", [])
            total_price = order_data.get("total_price")
            discount = order_data.get("discount")

        self.order_list.addItem("#### Order List ####")
        i = 0
        for item in orders:            
            i += 1
            self.order_list.addItem(f"{i}. {item['name']} ({item['price']})        x {item['qty']} [{item['status']}]")
        logger.info(f"total_price: {total_price}, discount: {discount}")
        if total_price is not None or discount is not None:
            current_text = self.menu_info.toPlainText()
            discount_info = ""
            total_price_info = ""
            if discount is not None:
                discount_info = f"\n💸 ส่วนลด: {discount} บาท"
                self.order_list.addItem(discount_info)
            if total_price is not None:
                total_price_info = f"\n💰 ราคารวมสุทธิ: {total_price} บาท"
                self.order_list.addItem(total_price_info)            
            
            self.menu_info.setText(f"{current_text}{discount_info}")

    def update_menu_info(self, name, desc):
        self.menu_info.setHtml(f"<h2>{name}</h2><p>{desc}</p>")

    def play_avatar_talking(self):
        self.avatar_movie.stop()
        self.avatar_movie.setFileName("./mira_client_pi/assets/avatar_pingping_v3.gif")
        self.avatar_movie.setScaledSize(
            self.avatar_movie.currentPixmap().size() * self.avatar_scale
        )
        self.avatar_scale = 1
        self.avatar_movie.start()

    def play_avatar_idle(self):
        self.avatar_movie.stop()
        self.avatar_movie.setFileName("./mira_client_pi/assets/pingping_static_v3.png")
        self.avatar_movie.setScaledSize(
            self.avatar_movie.currentPixmap().size() * self.avatar_scale
        )
        self.avatar_scale = 1
        self.avatar_movie.start()

    def handle_reply_ready(self, data):
        
        user_text = data.get("user_text", "")
        response_ssml = data.get("response_ssml", "")
        self.menu_info.setText(f"🧑‍💬: {user_text}\n🤖: {response_ssml}")
        # if "orders" in data:
        #     self.update_order_list(data["orders"])
        
        # if "total_price" in data or "discount" in data:
        #     current_text = self.menu_info.toPlainText()
        #     discount_info = ""
        #     if "discount" in data:
        #         discount_info = f"\n💸 ส่วนลด: {data['discount']} บาท"
        #     if "total_price" in data:
        #         discount_info += f"\n💰 ราคารวมสุทธิ: {data['total_price']} บาท"
        #     self.menu_info.setText(f"{current_text}{discount_info}")
        

# === Functions ===
def recognize_speech():
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=LANG,
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)

    def request_generator():
        while True:
            chunk = audio_queue.get()
            if chunk is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    responses = client.streaming_recognize(streaming_config, request_generator())

    for response in responses:
        for result in response.results:
            return result.alternatives[0].transcript



def fetch_orders():
    response = requests.get(ORDER_API_URL)
    return response.json()

def speak(text):
    tts = gTTS(text=text, lang='th')
    tts.save("output.mp3")
    os.system("mpg123 output.mp3")

# === Threaded Logic ===
# Removed main_loop and threading.Thread call

# === Main ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiraUI()
    window.show()

    sys.exit(app.exec_())
