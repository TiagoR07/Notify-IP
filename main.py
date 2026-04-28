import asyncio
import html
import os
import platform
import shutil
import socket
import subprocess
import sys

import discord
import psutil
import requests
from dotenv import load_dotenv

# =========================
# ENV SETUP (SAFE)
# =========================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
USER_ID_RAW = os.getenv("DISCORD_USER_ID", "").strip()

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in environment")

if not USER_ID_RAW.isdigit():
    raise RuntimeError("DISCORD_USER_ID must be a valid number")

USER_ID = int(USER_ID_RAW)

IS_WINDOWS = platform.system() == "Windows"


# =========================
# BASIC SAFETY LOGGING
# =========================

print("Bot starting...")
print(f"Platform: {platform.system()}")
print(f"User ID: {USER_ID}")


# =========================
# CONNECTION SAFETY
# =========================

async def wait_for_dns(host="discord.com"):
    for i in range(10):
        try:
            socket.gethostbyname(host)
            return
        except socket.gaierror:
            print(f"DNS fail attempt {i+1}")
            await asyncio.sleep(3)
    raise RuntimeError("DNS resolution failed")


# =========================
# SYSTEM INFO (SAFE CROSS-PLATFORM)
# =========================

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unknown"


def get_cpu_temp():
    if IS_WINDOWS:
        return None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read()) / 1000
    except:
        return None


def get_system_info():
    temp = get_cpu_temp()
    return (
        f"CPU Temp: {temp:.1f}°C" if temp else "CPU Temp: N/A"
    ) + "\n" + (
        f"CPU: {psutil.cpu_percent()}%"
    ) + "\n" + (
        f"RAM: {psutil.virtual_memory().percent}%"
    ) + "\n" + (
        f"Disk: {psutil.disk_usage('/').percent}%"
    ) + "\n" + (
        f"IP: {get_ip()}"
    )


# =========================
# BOT
# =========================

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

        if cmd == "system info":
            await message.channel.send(get_system_info())

        elif cmd == "shutdown" and not IS_WINDOWS:
            await message.channel.send("Shutting down...")
            subprocess.Popen(["sudo", "shutdown", "now"])

        elif cmd == "restart" and not IS_WINDOWS:
            await message.channel.send("Restarting...")
            subprocess.Popen(["sudo", "reboot"])

        elif cmd == "help":
            await message.channel.send(
                "Commands:\n"
                "- system info\n"
                "- shutdown\n"
                "- restart"
            )


# =========================
# GLOBAL ERROR SAFETY
# =========================

async def main():
    await wait_for_dns()

    intents = discord.Intents.default()
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