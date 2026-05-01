import asyncio
import sys

import discord

from config import TOKEN, USER_ID, IS_WINDOWS
from network import wait_for_dns, get_ip
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
                f"💬 Send `shutdown`, `restart`, `update`, `system info`, `disk usage`, or `speedtest` to this DM."
            )
        except Exception as e:
            print(f"Failed to send startup DM: {e}")

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


async def main():
    await wait_for_dns()

    intents = discord.Intents.all()
    intents.message_content = True
    intents.dm_messages = True

    client = MyClient(intents=intents)

    try:
        await client.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid token")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
