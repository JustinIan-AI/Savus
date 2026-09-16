"""loopdesk.channels — Channel adapter layer.

Adapters: Terminal, WebSocket, Slack, Feishu, Discord, Telegram.
"""

from loopdesk.channels.discord import DiscordChannel
from loopdesk.channels.feishu import FeishuChannel
from loopdesk.channels.manager import ChannelManager
from loopdesk.channels.slack import SlackChannel
from loopdesk.channels.telegram import TelegramChannel, TelegramChannelConfig
from loopdesk.channels.terminal import TerminalChannel
from loopdesk.channels.types import (
    Attachment,
    Channel,
    ChannelHealth,
    ChannelMeta,
    IncomingMessage,
    ManagedChannel,
    OutgoingMessage,
)
from loopdesk.channels.websocket import WebSocketChannel

__all__ = [
    # Protocol + types
    "Channel",
    "ManagedChannel",
    "ChannelHealth",
    "ChannelMeta",
    "IncomingMessage",
    "OutgoingMessage",
    "Attachment",
    # Manager
    "ChannelManager",
    # Adapters
    "TerminalChannel",
    "WebSocketChannel",
    "SlackChannel",
    "FeishuChannel",
    "DiscordChannel",
    "TelegramChannel",
    "TelegramChannelConfig",
]
