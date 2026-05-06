import asyncio
import logging
import sys

import discord
from discord import app_commands

from config import TOKEN, USER_ID, IS_WINDOWS
from network import wait_for_dns, get_ip
from system_info import get_cpu_temp
from bot.commands import handle_command
from bot.decorators import authorized_only

logger = logging.getLogger(__name__)


class MyClient(discord.Client):

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
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

    async def monitor(self):
        await self.wait_until_ready()

        while not self.is_closed():
            temp = get_cpu_temp()
            if temp and temp > 75:
                try:
                    user = await self.fetch_user(USER_ID)
                    await user.send(f"⚠️ High CPU temp: {temp:.1f}°C")
                except discord.HTTPException:
                    pass

            await asyncio.sleep(60)

    async def on_message(self, message):
        if message.author.id != USER_ID:
            return

        content = message.content.strip()

        if not content.startswith("!"):
            return

        cmd = content[1:].lower().strip()
        result = await handle_command(cmd, message)

        if result:
            await message.channel.send(result)

    async def setup_hook(self) -> None:
        commands = [
            ("system_info", "Get system information", "system info"),
            ("shutdown", "Shutdown the Raspberry Pi", "shutdown"),
            ("restart", "Restart the Raspberry Pi", "restart"),
            ("update", "Update system packages (apt)", "update"),
            ("disk_usage", "Show disk usage", "disk usage"),
            ("speedtest", "Run an internet speed test", "speedtest"),
            ("help", "Show available commands", "help"),
        ]

        for name, description, cmd in commands:
            @self.tree.command(name=name, description=description)
            @authorized_only
            async def _command(interaction: discord.Interaction, _cmd=cmd):
                await interaction.response.defer()
                result = await handle_command(_cmd, interaction)
                if result:
                    await interaction.followup.send(result)

        try:
            await self.tree.sync()
        except discord.HTTPException:
            pass


async def main():
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