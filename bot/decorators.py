from functools import wraps
from typing import Callable, Awaitable, Any
import discord
from config import USER_ID


def authorized_only(func: Callable[[discord.Interaction], Awaitable[Any]]) -> Callable[[discord.Interaction], Awaitable[Any]]:
    """Decorator to restrict command execution to the authorized user only.

    Args:
        func: The async function to wrap.

    Returns:
        A wrapped function that checks authorization before executing.
    """
    @wraps(func)
    async def wrapper(interaction: discord.Interaction, *args: Any, **kwargs: Any) -> Any:
        if interaction.user.id != USER_ID:
            await interaction.response.send_message("❌ Not authorized.", ephemeral=True)
            return
        return await func(interaction, *args, **kwargs)
    return wrapper