from pydantic import SecretStr
from langchain_mistralai import ChatMistralAI
from langchain_core.runnables import RunnableConfig

MODEL = "mistral-large-latest"

def _get_llm(config: RunnableConfig) -> ChatMistralAI:
    configurable = config.get("configurable") or {}
    user_key = configurable.get("api_key")
    if not user_key:
        raise ValueError("No api key provided")

    base_url = configurable.get("base_url")

    return ChatMistralAI(
        base_url=base_url,
        api_key=SecretStr(user_key),
        model=MODEL,
        default_headers={"X-Title": "Cura"},
    )
