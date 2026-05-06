import asyncio
import subprocess
import shutil
from typing import Union

from config import IS_WINDOWS
from system_info import get_system_info


async def _send_intermediate(source: Union["discord.Message", "discord.Interaction"], message: str):
    if hasattr(source, "channel"):
        await source.channel.send(message)
    else:
        await source.followup.send(message)


async def handle_command(cmd: str, source: Union["discord.Message", "discord.Interaction"]):
    # =========================
    # SYSTEM INFO
    # =========================
    if cmd == "system info":
        return get_system_info()

    # =========================
    # SHUTDOWN
    # =========================
    elif cmd == "shutdown":
        if IS_WINDOWS:
            return "❌ Shutdown is only available on Linux / Raspberry Pi."

        await asyncio.to_thread(subprocess.Popen, ["sudo", "shutdown", "now"])
        return "🛑 Shutting down the Raspberry Pi..."

    # =========================
    # RESTART
    # =========================
    elif cmd in ("restart", "reboot"):
        if IS_WINDOWS:
            return "❌ Restart is only available on Linux / Raspberry Pi."

        await asyncio.to_thread(subprocess.Popen, ["sudo", "reboot"])
        return "🔄 Restarting the Raspberry Pi..."

    # =========================
    # UPDATE (WITH OUTPUT)
    # =========================
    elif cmd == "update":
        if IS_WINDOWS:
            return "❌ Update via `apt` is only available on Linux / Raspberry Pi."

        await _send_intermediate(
            source,
            "🔄 Running `sudo apt update && sudo apt upgrade -y`...\nThis might take a while ⏳"
        )

        try:
            update_result = await asyncio.to_thread(
                subprocess.run,
                ["sudo", "apt", "update"],
                capture_output=True,
                text=True,
                timeout=800,
            )

            upgrade_result = await asyncio.to_thread(
                subprocess.run,
                ["sudo", "apt", "upgrade", "-y"],
                capture_output=True,
                text=True,
                timeout=2000,
            )

            combined_output = update_result.stdout + "\n" + upgrade_result.stdout

            last_lines = "\n".join(combined_output.strip().splitlines()[-30:])

            return f"✅ Update finished:\n```{last_lines}```"

        except Exception as e:
            return f"❌ Error while updating: {e}"

    # =========================
    # DISK USAGE (CLEAN OUTPUT)
    # =========================
    elif cmd == "disk usage":
        try:
            if IS_WINDOWS:
                total, used, free = shutil.disk_usage("/")
                return (
                    f"💽 Disk Usage:\n"
                    f"Total: {total // (2**30)} GB\n"
                    f"Used: {used // (2**30)} GB\n"
                    f"Free: {free // (2**30)} GB"
                )

            result = await asyncio.to_thread(
                subprocess.run,
                ["df", "-hT", "--exclude-type=tmpfs", "--exclude-type=devtmpfs"],
                capture_output=True,
                text=True,
                check=True,
            )

            lines = result.stdout.strip().split("\n")

            # keep only real disks
            filtered = [lines[0]]
            for line in lines[1:]:
                if line.startswith("/dev/"):
                    filtered.append(line)

            output = "\n".join(filtered)

            return f"💽 Disk Usage:\n```{output}```"

        except Exception as e:
            return f"❌ Could not get disk usage: {e}"

    # =========================
    # SPEEDTEST
    # =========================
    elif cmd == "speedtest":
        if not shutil.which("speedtest"):
            return "❌ `speedtest-cli` is not installed on this machine.\nInstall it with: `sudo apt install speedtest-cli`"

        await _send_intermediate(
            source,
            "📡 Running speed test... This might take a while ⏳"
        )

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["speedtest", "--simple"],
                capture_output=True,
                text=True,
                timeout=180,
            )

            return f"📡 Speed Test Results:\n```{result.stdout}```"

        except subprocess.TimeoutExpired:
            return "❌ Speed test timed out after 3 minutes. Try again later."
        except Exception as e:
            return f"❌ Error while running speed test: {e}"

    # =========================
    # HELP
    # =========================
    elif cmd == "help":
        return (
            "Here are the commands you can use:\n"
            "`system info`: Get system information.\n"
            "`disk usage`: Show disk usage.\n"
            "`speedtest`: Run an internet speed test.\n"
            "`update`: Update the system packages.\n"
            "`shutdown`: Shut down the Raspberry Pi.\n"
            "`restart`: Restart the Raspberry Pi.\n"
        )

    return None