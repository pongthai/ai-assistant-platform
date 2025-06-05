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
    update_orders = pyqtSignal(list)
    set_avatar_talking = pyqtSignal()
    set_avatar_idle = pyqtSignal()

    def run(self):
        self.update_text.emit("Listening...")
        audio_stream = AudioStream()
        audio_stream.start()
        try:
            text = recognize_speech()
            audio_stream.stop()
            self.update_text.emit(f"You said: {text}")
            self.set_avatar_talking.emit()
            result = ask_mira_server(text)
            speak(result['reply'])
            self.update_result.emit(result)
            orders = fetch_orders()
            self.update_orders.emit(orders)
        except Exception as e:
            print("Error:", e)
        finally:
            self.set_avatar_idle.emit()

# === UI ===
class MiraUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIRA Client")
        self.setGeometry(100, 100, 1024, 600)

        self.order_list = QListWidget()
        self.avatar_label = QLabel()
        self.avatar_movie = QMovie("pingping_static_v3.png")
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

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def update_order_list(self, orders):
        self.order_list.clear()
        for item in orders:
            self.order_list.addItem(f"{item['qty']} x {item['name']} [{item['status']}]")

    def update_menu_info(self, name, desc):
        self.menu_info.setHtml(f"<h2>{name}</h2><p>{desc}</p>")

    def play_avatar_talking(self):
        self.avatar_movie.stop()
        self.avatar_movie.setFileName("./mira/resources/avatar_pingping_v3.gif")
        self.avatar_movie.start()

    def play_avatar_idle(self):
        self.avatar_movie.stop()
        self.avatar_movie.setFileName("avatar_idle.gif")
        self.avatar_movie.start()

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


def ask_mira_server(text):
    response = requests.post(MIRA_SERVER_URL, json={"user_input": text})
    return response.json()

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