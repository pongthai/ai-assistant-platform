import os
from dotenv import load_dotenv
load_dotenv()  # โหลดจาก .env อัตโนมัติ

# Add from client side

# ✅ General settings
PROJECT_NAME = "Smart Assistant - Core"

DEBUG_MODE = True
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ✅ Server Settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_TONE = os.getenv("SYSTEM_TONE", "family")
TTS_SERVER_ENDPOINT = "http://192.168.100.101:8000/api/shared/speak"

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
TEMP_AUDIO_PATH = "/tmp"
SAMPLE_RATE = 48000
AUDIO_DTYPE="float32"
AVATAR_STATIC = "pingping_static_v3.png"
AVATAR_ANIMATION = "pingping_animation_v3.gif"
PROCESSING_SOUND_FILE="./core/audio/processing_sound.mp3"
SESSION_ID = os.getenv("SESSION_ID", "rasp-pi-001")
