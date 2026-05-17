import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import wraps
from typing import Any

import discord

from bot.constants import (
    ERR_NOT_AUTHORIZED,
    LOG_AUTHORIZED_SLASH,
    LOG_UNAUTHORIZED_SLASH,
)
from config import USER_ID

logger = logging.getLogger(__name__)


def authorized_only(
    func: Callable[[discord.Interaction], Awaitable[Any]],
) -> Callable[[discord.Interaction], Awaitable[Any]]:
    """Decorator to restrict command execution to the authorized user only.

    Args:
        func: The async function to wrap.

    Returns:
        A wrapped function that checks authorization before executing.
    """

    @wraps(func)
    async def wrapper(interaction: discord.Interaction, *args: Any, **kwargs: Any) -> Any:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = interaction.user
        command_name = interaction.command.name if interaction.command else "unknown"

        if interaction.user.id != USER_ID:
            logger.warning(
                LOG_UNAUTHORIZED_SLASH.format(
                    timestamp=timestamp, user=user, user_id=user.id, command=command_name
                )
            )
            await interaction.response.send_message(ERR_NOT_AUTHORIZED, ephemeral=True)
            return

        logger.info(
            LOG_AUTHORIZED_SLASH.format(
                timestamp=timestamp, user=user, user_id=user.id, command=command_name
            )
        )
        return await func(interaction, *args, **kwargs)

    return wrapper
