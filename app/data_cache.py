"""Reusable caching helpers for CreditX."""

from __future__ import annotations

from functools import lru_cache, wraps
from typing import Any, Callable, Iterable, Tuple, TypeVar

PricingResult = Tuple[int, Tuple[str, ...]]
P = TypeVar("P")
R = TypeVar("R")


def cache_pricing(func: Callable[..., PricingResult]) -> Callable[..., PricingResult]:
    """LRU cache decorator tuned for pricing computations."""

    cached_func = lru_cache(maxsize=1024)(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> PricingResult:
        return cached_func(*args, **kwargs)

    wrapper.cache_clear = cached_func.cache_clear  # type: ignore[attr-defined]
    return wrapper


def lru_cached(maxsize: int = 256) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Generic LRU cache decorator for other expensive helpers."""

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        cached_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            return cached_func(*args, **kwargs)

        wrapper.cache_clear = cached_func.cache_clear  # type: ignore[attr-defined]
        return wrapper

    return decorator


__all__ = ["cache_pricing", "lru_cached"]
