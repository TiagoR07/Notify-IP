from functools import wraps
from config import USER_ID


def authorized_only(func):
    @wraps(func)
    async def wrapper(interaction, *args, **kwargs):
        if interaction.user.id != USER_ID:
            await interaction.response.send_message("❌ Not authorized.", ephemeral=True)
            return
        return await func(interaction, *args, **kwargs)
    return wrapper