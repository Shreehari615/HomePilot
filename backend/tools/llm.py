"""
HomePilot AI — LLM Factory

Creates and manages the Chat Model instance. Supports OpenAI
as the provider (configured via LLM_PROVIDER env var).
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from config import get_settings
from utils.logger import get_logger, log_llm_call

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """
    Get or create the shared Chat Model instance.

    Supports 'openai' provider via LLM_PROVIDER env var.
    Returns a cached singleton to avoid re-initializing on every call.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider != "openai":
        raise ValueError(
            f"Unknown or unsupported LLM_PROVIDER '{provider}'. Only 'openai' is supported."
        )

    from langchain_openai import ChatOpenAI
    model_name = settings.openai_model
    logger.info("llm_initialized", provider="openai", model=model_name)
    kwargs = {
        "model": model_name,
        "api_key": settings.openai_api_key,
        "temperature": 0.3,
        "max_retries": 3,
        "request_timeout": 180,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
        
    return ChatOpenAI(**kwargs)


def get_model_name() -> str:
    """Get the current model name for logging."""
    settings = get_settings()
    return settings.openai_model


async def invoke_llm(
    messages: list[dict[str, str]],
    purpose: str = "general",
) -> str:
    """
    Invoke the LLM with timing and usage logging.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        purpose:  Description of why this call is being made (for logging).

    Returns:
        The LLM's response content as a string.
    """
    llm = get_llm()
    start = time.perf_counter()

    try:
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        lc_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        response = await llm.ainvoke(lc_messages)
        elapsed = (time.perf_counter() - start) * 1000

        # Log the call
        usage = getattr(response, "usage_metadata", None)
        log_llm_call(
            model=get_model_name(),
            prompt_tokens=usage.get("input_tokens") if usage else None,
            completion_tokens=usage.get("output_tokens") if usage else None,
            duration_ms=elapsed,
            purpose=purpose,
        )

        return response.content

    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        logger.error(
            "llm_invocation_failed",
            purpose=purpose,
            duration_ms=round(elapsed, 2),
            error=str(e),
        )
        raise
