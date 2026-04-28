import asyncio
import discord

from config import USER_ID
from network import get_ip
from system_info import get_cpu_temp
from bot.commands import handle_command

class MyClient(discord.Client):

    async def on_ready(self):
        print(f"Logged in as {self.user}")

        try:
            user = await self.fetch_user(USER_ID)
            ip = get_ip()
            await user.send(
                f"🔌 Hey <@{USER_ID}>! Your Raspberry Pi is online!\n"
                f"🌐 IP Address: `{ip}`\n"
                f"💬 Send `shutdown`, `restart`, `system info`, or `help`."
            )
        except Exception as e:
            print(f"Failed to send startup DM: {e}")

        # start monitor loop
        self.loop.create_task(self.monitor())

    async def monitor(self):
        await self.wait_until_ready()

        while not self.is_closed():
            temp = get_cpu_temp()
            if temp and temp > 75:
                try:
                    user = await self.fetch_user(USER_ID)
                    await user.send(f"⚠️ High CPU temp: {temp:.1f}°C")
                except:
                    pass

            await asyncio.sleep(60)

    async def on_message(self, message):
        if message.author.id != USER_ID:
            return

        cmd = message.content.lower().strip()

        result = await handle_command(cmd, message)

        if result:
            await message.channel.send(result)