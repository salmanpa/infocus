"""Data classes and simple utilities for Telegram fetching."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ChannelConfig:
    """Configuration for a Telegram channel to fetch posts from."""

    username: str
    limit: int = 50

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("Channel message limit must be positive")


@dataclass(frozen=True)
class TelegramMessage:
    """Normalized Telegram message representation for downstream processing."""

    message_id: int
    channel: str
    text: str
    posted_at: datetime
    link: Optional[str] = None

    def to_dict(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "channel": self.channel,
            "text": self.text,
            "posted_at": self.posted_at.isoformat(),
            "link": self.link,
        }
