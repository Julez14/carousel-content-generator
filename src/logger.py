"""Discord webhook logger for TikTok carousel bot."""

from __future__ import annotations

import json
import requests
from datetime import datetime
from typing import Any


class DiscordWebhookLogger:
    """Logger that sends messages to Discord webhook with embeds."""

    def __init__(self, webhook_url: str) -> None:
        """Initialize the Discord webhook logger.
        
        Args:
            webhook_url: Discord webhook URL for sending messages.
        """
        self.webhook_url = webhook_url

    def _send_embed(self, title: str, description: str, color: int) -> None:
        """Send an embed message to Discord.
        
        Args:
            title: Embed title.
            description: Embed description.
            color: Embed color (integer format).
        """
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            # Fallback to simple text message if embed fails
            fallback_payload = {
                "content": f"**{title}**\n{description}"
            }
            try:
                requests.post(
                    self.webhook_url,
                    json=fallback_payload,
                    timeout=10
                )
            except Exception:
                # Silent fail - don't want logging to break the main process
                pass

    def info(self, message: str, account: str | None = None) -> None:
        """Log an info message.
        
        Args:
            message: Message to log.
            account: Optional account name for context.
        """
        title = "✅ TikTok Carousel - Success"
        if account:
            title += f" ({account})"
        
        self._send_embed(
            title=title,
            description=message,
            color=0x00FF00  # Green
        )

    def error(self, message: str, account: str | None = None, error: Exception | None = None) -> None:
        """Log an error message.
        
        Args:
            message: Error message to log.
            account: Optional account name for context.
            error: Optional exception for additional details.
        """
        title = "❌ TikTok Carousel - Error"
        if account:
            title += f" ({account})"
        
        description = message
        if error:
            description += f"\n\n**Error Details:**\n```{str(error)}```"
        
        self._send_embed(
            title=title,
            description=description,
            color=0xFF0000  # Red
        )

    def warning(self, message: str, account: str | None = None) -> None:
        """Log a warning message.
        
        Args:
            message: Warning message to log.
            account: Optional account name for context.
        """
        title = "⚠️ TikTok Carousel - Warning"
        if account:
            title += f" ({account})"
        
        self._send_embed(
            title=title,
            description=message,
            color=0xFFFF00  # Yellow
        ) 