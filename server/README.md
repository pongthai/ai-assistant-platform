# Server for AI Assistant Platform

This FastAPI backend handles:
- ChatGPT interaction
- Memory and intent routing
- TTS and token usage tracking

ai-assistant-platform/
│
├── server/
│   ├── api_server.py                  ← จุดเริ่มต้น FastAPI
│   ├── routes/
│   │   ├── pingping_routes.py         ← route เฉพาะของ PingPing
│   │   ├── vera_routes.py             ← route เฉพาะของ VERA
│   │   ├── mira_routes.py             ← route เฉพาะของ MIRA
│   │   └── shared_routes.py           ← endpoint ที่ใช้ร่วมกัน (health check, TTS, STT)
│   │
│   ├── clients/
│   │   ├── pingping_client_handler.py ← logic/flow ของ PingPing
│   │   ├── vera_client_handler.py     ← logic/flow ของ VERA
│   │   └── mira_client_handler.py     ← logic/flow ของ MIRA
│   │
│   ├── core/
│   │   ├── gpt_proxy.py               ← ส่งคำถามไป ChatGPT/OpenAI
│   │   ├── intent_router.py           ← จัดการ intent classification
│   │   ├── command_handler.py         ← จัดการคำสั่ง Home Assistant
│   │   └── tts_stt/
│   │       ├── tts_manager.py
│   │       └── stt_manager.py
│   │
│   ├── config/
│   │   └── settings.py                ← สำหรับ config เช่น client_type, API keys
│   │
│   └── utils/
│       └── logger.py

## Run the server:
```bash
uvicorn server.main:app --reload
