"""
HomePilot AI — Structured Logging

Provides a configured structlog logger that outputs JSON in production
and human-readable colored logs in development. Logs LLM calls, tool
executions, errors, and timing information.
"""

from __future__ import annotations

import sys
import time
import logging
from functools import wraps
from typing import Any, Callable

import structlog

from config import get_settings


def setup_logging() -> None:
    """Configure structlog and stdlib logging for the application."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Determine renderer based on environment
    if settings.app_env == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog as well
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a named logger instance.

    Args:
        name: Logger name, typically the module name.

    Returns:
        A bound structlog logger.
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(module=name)
    return logger


def log_llm_call(
    model: str,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    duration_ms: float | None = None,
    **kwargs: Any,
) -> None:
    """Log an LLM API call with usage metrics."""
    logger = get_logger("llm")
    logger.info(
        "llm_call",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration_ms=round(duration_ms, 2) if duration_ms else None,
        **kwargs,
    )


def log_tool_call(
    tool_name: str,
    input_data: dict | None = None,
    output_summary: str | None = None,
    duration_ms: float | None = None,
    success: bool = True,
    **kwargs: Any,
) -> None:
    """Log a tool execution with timing and result summary."""
    logger = get_logger("tools")
    log_method = logger.info if success else logger.error
    log_method(
        "tool_call",
        tool=tool_name,
        input=input_data,
        output_summary=output_summary,
        duration_ms=round(duration_ms, 2) if duration_ms else None,
        success=success,
        **kwargs,
    )


def timed(func: Callable) -> Callable:
    """
    Decorator that logs the execution time of a function.

    Works with both sync and async functions.
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(
                "function_executed",
                function=func.__name__,
                duration_ms=round(elapsed, 2),
            )
            return result
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "function_failed",
                function=func.__name__,
                duration_ms=round(elapsed, 2),
                error=str(exc),
            )
            raise

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(
                "function_executed",
                function=func.__name__,
                duration_ms=round(elapsed, 2),
            )
            return result
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "function_failed",
                function=func.__name__,
                duration_ms=round(elapsed, 2),
                error=str(exc),
            )
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
