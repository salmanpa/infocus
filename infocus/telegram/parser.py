"""Base Telegram parser module for fetching channel news."""
from __future__ import annotations

from datetime import datetime
from typing import Sequence

from .client import ChannelConfig, TelegramMessage


class TelethonClientFactory:
    """Factory for creating Telethon clients with shared configuration."""

    def __init__(self, api_id: int, api_hash: str, session_name: str = "infocus") -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name

    @classmethod
    def from_env(cls, session_name: str = "infocus") -> "TelethonClientFactory":
        api_id_env = "TELEGRAM_API_ID"
        api_hash_env = "TELEGRAM_API_HASH"
        try:
            api_id = int(_require_env(api_id_env))
        except ValueError as exc:  # pragma: no cover - thin validation branch
            raise ValueError(f"{api_id_env} must be an integer") from exc
        api_hash = _require_env(api_hash_env)
        return cls(api_id=api_id, api_hash=api_hash, session_name=session_name)

    def build(self):
        from telethon import TelegramClient

        return TelegramClient(self.session_name, self.api_id, self.api_hash)


class TelegramNewsParser:
    """Basic parser for fetching posts from Telegram channels."""

    def __init__(self, client_factory: TelethonClientFactory) -> None:
        self.client_factory = client_factory

    async def fetch_channel_messages(self, channel: ChannelConfig) -> list[TelegramMessage]:
        client = self.client_factory.build()
        await client.connect()
        try:
            messages: list[TelegramMessage] = []
            async for message in client.iter_messages(channel.username, limit=channel.limit):
                if not message.message:
                    continue
                messages.append(
                    TelegramMessage(
                        message_id=message.id,
                        channel=channel.username,
                        text=message.message,
                        posted_at=message.date or datetime.utcnow(),
                        link=_build_message_link(channel.username, message.id),
                    )
                )
        finally:
            await client.disconnect()
        messages.reverse()
        return messages

    async def fetch_many(self, channels: Sequence[ChannelConfig]) -> list[TelegramMessage]:
        items: list[TelegramMessage] = []
        for channel in channels:
            items.extend(await self.fetch_channel_messages(channel))
        return items


def _build_message_link(username: str, message_id: int) -> str:
    return f"https://t.me/{username}/{message_id}"


def _require_env(name: str) -> str:
    from os import getenv

    value = getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required for Telegram API access")
    return value
