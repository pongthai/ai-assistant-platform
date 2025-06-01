from server.mira.services.session_manager import session_manager
from openai import OpenAI
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL
from core.utils.logger_config import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)


def ask_gpt(session_id: str, user_message: str) -> str:
    logger.info("Sending conversation to OpenAI")

    messages = []

    # ดึง system prompt และ summarized history
    system_prompt = session_manager.get_system_prompt(session_id)
    summary_text = session_manager.get_summary_text(session_id).strip()
    history = session_manager.get_history(session_id)

    # รวมเข้าไปใน system message ถ้ามี
    combined_system_prompt = system_prompt or ""
    if summary_text:
        combined_system_prompt += f"\n\n[สรุปบทสนทนาก่อนหน้า]:\n{summary_text}"
    if combined_system_prompt:
        messages.append({"role": "system", "content": combined_system_prompt})

    # เพิ่ม history หากมี
    messages.extend(history)

    # เพิ่มข้อความใหม่ของผู้ใช้
    messages.append({"role": "user", "content": user_message})
    #logger.debug(f"Messages: {messages}")

    # Call OpenAI
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    usage = response.usage
    logger.info(f"🔢 Token usage: input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    return reply

# Summarization function
def gpt_summarize(text: str) -> str:
    logger.info("Sending summarization request to OpenAI")
    messages = [
        {"role": "system", "content": "กรุณาสรุปเนื้อหาต่อไปนี้อย่างสั้นและชัดเจน โดยไม่ใส่แท็ก SSML หรือโค้ดใด ๆ"},
        {"role": "user", "content": text}
    ]
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    summary = response.choices[0].message.content.strip()
    usage = response.usage
    logger.info(f"🔢 Token usage (summary): input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    return summary
