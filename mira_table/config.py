# Configuration for client-side settings

# Initial greeting
INIT_GREETING = "สวัสดีค่ะ วันนี้มีอะไรให้ MIRA ช่วยบ้างตะ MIRA สามารถแนะนำเมนนูอร่อยๆให้ได้นะ"

# Server endpoint
SERVER_HOST = "http://localhost:8000/api/mira"

# Audio settings (if needed later)
INPUT_DEVICE_INDEX = None  # หรือกำหนดเป็น index ของ mic เฉพาะ
OUTPUT_DEVICE_INDEX = None


SESSION_ID="mira-session-001"

# Timeout or retry logic
RETRY_COUNT = 3
RETRY_DELAY = 1.0
