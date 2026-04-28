import subprocess
import shutil

from config import IS_WINDOWS
from system_info import get_system_info


async def handle_command(cmd, message):
    # =========================
    # SYSTEM INFO
    # =========================
    if cmd == "system info":
        return f"📊 System Info:\n{get_system_info()}"

    # =========================
    # SHUTDOWN
    # =========================
    elif cmd == "shutdown":
        if IS_WINDOWS:
            return "❌ Shutdown is only available on Linux / Raspberry Pi."

        subprocess.Popen(["sudo", "shutdown", "now"])
        return "🛑 Shutting down the Raspberry Pi..."

    # =========================
    # RESTART
    # =========================
    elif cmd == "restart":
        if IS_WINDOWS:
            return "❌ Restart is only available on Linux / Raspberry Pi."

        subprocess.Popen(["sudo", "reboot"])
        return "🔄 Restarting the Raspberry Pi..."

    # =========================
    # UPDATE (WITH OUTPUT)
    # =========================
    elif cmd == "update":
        if IS_WINDOWS:
            return "❌ Update via `apt` is only available on Linux / Raspberry Pi."

        await message.channel.send(
            "🔄 Running `sudo apt update && sudo apt upgrade -y`...\nThis might take a while ⏳"
        )

        try:
            update_result = subprocess.run(
                ["sudo", "apt", "update"],
                capture_output=True,
                text=True,
                timeout=800,
            )

            upgrade_result = subprocess.run(
                ["sudo", "apt", "upgrade", "-y"],
                capture_output=True,
                text=True,
                timeout=2000,
            )

            combined_output = update_result.stdout + "\n" + upgrade_result.stdout

            # last 30 lines (clean output)
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

            result = subprocess.run(
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
    # HELP
    # =========================
    elif cmd == "help":
        return (
            "Here are the commands you can use:\n"
            "`system info`: Get system information.\n"
            "`disk usage`: Show disk usage.\n"
            "`update`: Update the system packages.\n"
            "`shutdown`: Shut down the Raspberry Pi.\n"
            "`restart`: Restart the Raspberry Pi.\n"
        )

    return None