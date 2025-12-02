from llama_index.llms.openai_like import OpenAILike
from app.core.config import settings


def get_llm() -> OpenAILike:
    return OpenAILike(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.LLM_API_KEY,
        api_base=settings.LLM_BASE_URL,
        temperature=0.7,
        is_chat_model=True,
        is_function_calling_model=True,
    )
