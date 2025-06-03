import asyncio
from server.mira.services.session_manager import session_manager
from server.mira.services.prompt_builder import PromptBuilder
from openai import OpenAI
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL
from core.utils.logger_config import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)


async def ask_gpt(session_id: str, user_message: str) -> str:
    session_manager.add_user_message(session_id, user_message)
    prompt_builder = PromptBuilder()
    order_list = session_manager.get_order_list(session_id)
    logger.debug(f"ORDER_LIST = {order_list}")
    user_prompt = prompt_builder.build_user_prompt(user_message, order_list)
    messages = await session_manager.get_full_context(session_id, max_history=5)

        # Convert messages to structured format for gpt-4o / gpt-4o-mini
    for msg in messages:
        if isinstance(msg.get("content"), str):
            msg["content"] = [{"type": "text", "text": msg["content"]}]

    messages.append({
        "role": "user",
        "content": [{"type": "text", "text": user_prompt}]
    })
    logger.debug(f"Total context messages: {len(messages)}")
    logger.debug(f"User prompt: {user_prompt}")
    logger.debug(f"Messages to be sent: {messages}")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    session_manager.add_assistant_reply(session_id, reply)
    asyncio.create_task(session_manager.summarize_if_needed(session_id))
    usage = response.usage
    logger.info(f"🔢 Token usage: input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
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
