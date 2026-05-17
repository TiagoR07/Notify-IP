import asyncio
import logging
import sys
from datetime import datetime
from typing import Any

import discord
from discord import app_commands

from bot.commands import handle_command
from bot.constants import (
    CMD_DISK_USAGE,
    CMD_HELP,
    CMD_RESTART,
    CMD_SHUTDOWN,
    CMD_SPEEDTEST,
    CMD_SYSTEM_INFO,
    CMD_UPDATE,
    CMD_FIX_PERMS,
    CMD_RESTART_AVAHI,
    LOG_UNAUTHORIZED_PREFIX,
    LOG_AUTHORIZED_PREFIX,
)
from bot.decorators import authorized_only
from config import CPU_TEMP_WARNING_THRESHOLD, TOKEN, USER_ID
from network import get_ip, wait_for_dns
from system_info import get_cpu_temp

logger = logging.getLogger(__name__)


class MyClient(discord.Client):
    """Discord bot client for system monitoring and control."""

    def __init__(self, *, intents: discord.Intents):
        """Initialize the Discord client.

        Args:
            intents: Discord intents for the bot.
        """
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        """Handle the bot ready event.

        Sends a startup DM with the IP address and starts monitoring.
        """
        logger.info(f"Logged in as {self.user}")

        try:
            user = await self.fetch_user(USER_ID)
            ip = get_ip()
            await user.send(
                f"🔌 Hey <@{USER_ID}>! Your Raspberry Pi is online!\n"
                f"🌐 IP Address: `{ip}`\n"
                f"💬 You can use slash commands (try `/system_info`) — slash commands give autocomplete. `!`-prefixed commands still work as a fallback."
            )
        except Exception as e:
            logger.error(f"Failed to send startup DM: {e}")

        self.loop.create_task(self.monitor())

    async def monitor(self) -> None:
        """Monitor CPU temperature and send warnings if it exceeds the threshold.

        Checks temperature every 60 seconds.
        """
        await self.wait_until_ready()

        while not self.is_closed():
            temp = get_cpu_temp()
            if temp and temp > CPU_TEMP_WARNING_THRESHOLD:
                try:
                    user = await self.fetch_user(USER_ID)
                    await user.send(f"⚠️ High CPU temp: {temp:.1f}°C")
                except discord.HTTPException as e:
                    logger.warning(f"Failed to send temp warning: {e}")

            await asyncio.sleep(60)

    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages.

        Processes commands prefixed with '!' from the authorized user.

        Args:
            message: The Discord message to process.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = message.author

        if message.author.id != USER_ID:
            content = message.content.strip()
            if content.startswith("!"):
                cmd = content[1:].lower().strip()
                logger.warning(
                    LOG_UNAUTHORIZED_PREFIX.format(
                        timestamp=timestamp, user=user, user_id=user.id, command=cmd
                    )
                )
            return

        content = message.content.strip()

        if not content.startswith("!"):
            return

        cmd = content[1:].lower().strip()
        logger.info(
            LOG_AUTHORIZED_PREFIX.format(
                timestamp=timestamp, user=user, user_id=user.id, command=cmd
            )
        )
        result = await handle_command(cmd, message)

        if result:
            await message.channel.send(result)

    async def setup_hook(self) -> None:
        """Set up slash commands and sync them with Discord.

        Registers all available commands and syncs them with Discord's API.
        """
        commands = [
            ("system_info", "Get system information", CMD_SYSTEM_INFO),
            ("shutdown", "Shutdown the Raspberry Pi", CMD_SHUTDOWN),
            ("restart", "Restart the Raspberry Pi", CMD_RESTART),
            ("update", "Update system packages (apt)", CMD_UPDATE),
            ("disk_usage", "Show disk usage", CMD_DISK_USAGE),
            ("speedtest", "Run an internet speed test", CMD_SPEEDTEST),
            ("fix_permissions", "Fix file permissions", CMD_FIX_PERMS),
            ("restart_avahi", "Restart the avahi-daemon service", CMD_RESTART_AVAHI),
            ("help", "Show available commands", CMD_HELP),
        ]

        def make_command_handler(cmd: str):
            """Create a command handler for a specific command.

            Args:
                cmd: The command string to execute.

            Returns:
                An async handler function for the command.
            """

            @authorized_only
            async def handler(interaction: discord.Interaction[Any]) -> None:
                await interaction.response.defer()
                result = await handle_command(cmd, interaction)
                if result:
                    await interaction.followup.send(result)

            return handler

        for name, description, cmd in commands:
            self.tree.command(name=name, description=description)(make_command_handler(cmd))

        try:
            await self.tree.sync()
        except discord.HTTPException as e:
            logger.warning(f"Failed to sync commands: {e}")


async def main():
    """Main entry point for the Discord bot.

    Waits for DNS resolution, initializes the client, and starts the bot.
    """
    await wait_for_dns()

    intents = discord.Intents.all()
    intents.message_content = True
    intents.dm_messages = True

    client = MyClient(intents=intents)

    try:
        await client.start(TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid token")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
