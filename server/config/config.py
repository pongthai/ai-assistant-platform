
import os
from dotenv import load_dotenv
load_dotenv()


# ✅ General settings
PROJECT_NAME = "HANA - Server"
LOG_LEVEL = "DEBUG"

# ✅ Server Settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_TONE = os.getenv("SYSTEM_TONE", "family")
HA_URL = os.getenv("HA_URL", "http://192.168.100.101:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

# ✅ Client Settings
GPT_SERVER_ENDPOINT = os.getenv("GPT_SERVER_ENDPOINT", "http://192.168.100.101:8000/chat")
TTS_SERVER_ENDPOINT = os.getenv("TTS_SERVER_ENDPOINT", "http://192.168.100.101:8000/chat")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/Workspace/smart-assistant-client-server/server/gctts_key.json")

TTS_PATH = os.getenv("TTS_PATH", ".")

TTS_PROVIDER="GoogleCloudTTS"

TUYA_ACCESS_ID = os.getenv("TUYA_ACCESS_ID", "")
TUYA_ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY", "")
TUYA_API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT", "https://openapi.tuyaus.com")

# ✅ Static keywords
WAKE_WORDS = ["ผิงผิง", "สวัสดีผิงผิง", "ทดสอบ"]
COMMAND_WORDS = {
    "stop": ["หยุดพูด", "หยุด", "เงียบ"],
    "exit": ["ออกจากโปรแกรม", "เลิกทำงาน"]
}
CONFIRMATION_KEYWORDS = ["ใช่", "ใช่แล้ว","ใช่จ้า", "ใช่ครับ", "ใช่ค่ะ", "ใช่เลย",  "ตกลง", "โอเค", "ได้เลย"]
CANCEL_KEYWORDS = ["ไม่ใช่", "ไม่ใช่จ้า","ไม่ใช่นะ","ไม่ใช่ครับ","ไม่ใช่ค่ะ","ไม่", "ยกเลิก", "หยุด"]

ACTION_KEYWORDS = {
    "เปิด": ["เปิด", "เปิดไฟ", "เปิดสวิตช์", "เปิดปลั๊ก"],
    "ปิด": ["ปิด", "ปิดไฟ", "ปิดสวิตช์", "ปิดปลั๊ก"],
    "เพิ่ม": ["เพิ่ม", "เพิ่มเสียง", "เพิ่มแสง"],
    "ลด": ["ลด", "ลดเสียง", "ลดแสง"],
    "ตั้ง": ["ตั้ง", "ตั้งเวลา", "ตั้งอุณหภูมิ"],
    "หยุด": ["หยุด", "ปิดเสียง", "หยุดเพลง"]
}
STOP_WORDS = ["หยุดพูด","หยุด", "เงียบ", "พอแล้ว"]
EXIT_WORDS = ["ออกจากโปรแกรม", "เลิกทำงาน"]

# ✅ Misc
IDLE_TIMEOUT = 60
HELLO_MSG = "ว่าไงจ๊ะ"
ENABLE_AVATAR_DISPLAY = True
AVATAR_SCALE = 1.0
TEMP_AUDIO_PATH = "/dev/shm"
SAMPLE_RATE = 48000
AVATAR_STATIC = "pingping_static_v3.png"
AVATAR_ANIMATION = "pingping_animation_v3.gif"
SESSION_ID = os.getenv("SESSION_ID", "rasp-pi-001")