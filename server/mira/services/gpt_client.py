from openai import OpenAI
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL
from core.utils.logger_config import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(messages: list) -> str:
    logger.info("Sending conversation to OpenAI")
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    usage = response.usage
    logger.info(f"🔢 Token usage: input={usage.prompt_tokens}, output={usage.completion_tokens}, total={usage.total_tokens}")
    return reply
