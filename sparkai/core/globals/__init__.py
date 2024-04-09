# flake8: noqa
"""Global values and configuration that apply to all of SparkAI."""
import warnings
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sparkai.core.caches import BaseCache


_verbose: bool = False
_debug: bool = False
_llm_cache: Optional["BaseCache"] = None


def set_verbose(value: bool) -> None:

    global _verbose
    _verbose = value


def get_verbose() -> bool:
    old_verbose = False

    global _verbose
    return _verbose or old_verbose


def set_debug(value: bool) -> None:

    global _debug
    _debug = value


def get_debug() -> bool:
    old_debug = False

    global _debug
    return _debug or old_debug


def set_llm_cache(value: Optional["BaseCache"]) -> None:

    global _llm_cache
    _llm_cache = value


def get_llm_cache() -> "BaseCache":
    """Get the value of the `llm_cache` global setting."""
    old_llm_cache = None
    global _llm_cache
    return _llm_cache or old_llm_cache
