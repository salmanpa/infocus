"""Telegram-specific utilities for InFocus."""

from .client import ChannelConfig, TelegramMessage
from .parser import TelegramNewsParser, TelethonClientFactory

__all__ = [
    "ChannelConfig",
    "TelegramMessage",
    "TelegramNewsParser",
    "TelethonClientFactory",
]
