import asyncio
import json
from server.mira.services.session_manager import session_manager
from server.mira.services.prompt_builder import PromptBuilder
from openai import OpenAI
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL
from core.utils.logger_config import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

prompt_builder = PromptBuilder()

async def detect_intent(user_message: str) -> dict:
    prompt = prompt_builder.build_intent_detection_prompt(user_message)
    messages = [
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    ]
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    usage = response.usage
    logger.info(f"🔢 Token usage (intent detection): input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    try:
        result = response.choices[0].message.content.strip()
        intent_data = json.loads(result)
        return intent_data
    except Exception as e:
        logger.warning(f"Failed to parse intent response: {e}")
        return {"intent": "unknown", "confidence": 0.0, "menu_scope": "n/a"}

async def ask_gpt(session_id: str, user_message: str) -> str:
    # Initialize session if needed
    if session_manager.is_fresh(session_id):
        init_prompt = prompt_builder.build_init_prompt()
        session_manager.init_session(session_id, system_prompt=init_prompt)

    # 1. Detect coarse intent (Tier-1)
    intent_data = await detect_intent(user_message)
    coarse_intent = intent_data.get("intent", "unknown")
    menu_scope = intent_data.get("menu_scope", "n/a")
    logger.debug(f"Detected intent: {intent_data}")

    # 2. Build user prompt by intent
    order_list = session_manager.get_order_list(session_id)
    user_prompt = prompt_builder.build_prompt_by_intent(coarse_intent,  user_message, order_list, menu_scope=menu_scope)

    # 3. Store user message
    session_manager.add_user_message(session_id, user_message)

    # 4. Context
    messages = await session_manager.get_full_context(session_id, max_history=5)
    messages.append({
        "role": "user",
        "content": [{"type": "text", "text": user_prompt}]
    })

    # 5. Normalize format
    for msg in messages:
        if isinstance(msg.get("content"), str):
            msg["content"] = [{"type": "text", "text": msg["content"]}]
    
    logger.debug(f"User prompt: {user_prompt}")
    logger.debug(f"Messages to be sent: {messages}")

    # 6. Send to GPT
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    session_manager.add_assistant_reply(session_id, reply)
    asyncio.create_task(session_manager.summarize_if_needed(session_id))
    usage = response.usage
    logger.info(f"🔢 Token usage (ask_gpt): input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    return reply

# Summarization function
async def gpt_summarize(text: str) -> str:
    logger.info("Sending summarization request to OpenAI")
    logger.debug(f"📝 Text to summarize: {text}")
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "กรุณาสรุปเนื้อหาต่อไปนี้อย่างสั้นและชัดเจน โดยไม่ใส่แท็ก SSML หรือโค้ดใด ๆ"}]
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": text}]
        }
    ]
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    summary = response.choices[0].message.content.strip()
    usage = response.usage
    logger.info(f"🔢 Token usage (summary): input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    return summary
