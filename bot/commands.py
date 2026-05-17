from __future__ import annotations

import asyncio
import shutil
import subprocess
from collections.abc import Awaitable, Callable

import discord

from bot.constants import (
    CMD_DISK_USAGE,
    CMD_FIX_PERMS,
    CMD_HELP,
    CMD_REBOOT,
    CMD_RESTART,
    CMD_RESTART_AVAHI,
    CMD_SHUTDOWN,
    CMD_SPEEDTEST,
    CMD_SYSTEM_INFO,
    CMD_UPDATE,
    ERR_DISK_USAGE,
    ERR_FIX_PERMS,
    ERR_RESTART_AVAHI,
    ERR_SPEEDTEST_ERROR,
    ERR_SPEEDTEST_NOT_INSTALLED,
    ERR_SPEEDTEST_TIMEOUT,
    ERR_UPDATE,
    ERR_WINDOWS_ONLY,
    HELP_MESSAGE,
    MSG_DISK_USAGE,
    MSG_DISK_USAGE_WINDOWS,
    MSG_FIX_PERMS_DONE,
    MSG_RESTART,
    MSG_RESTART_AVAHI_DONE,
    MSG_SHUTDOWN,
    MSG_SPEEDTEST_RESULTS,
    MSG_SPEEDTEST_START,
    MSG_UPDATE_DONE,
    MSG_UPDATE_START,
)
from config import APT_UPDATE_TIMEOUT, APT_UPGRADE_TIMEOUT, IS_WINDOWS, SPEEDTEST_TIMEOUT
from system_info import get_system_info


async def respond(source: discord.Message | discord.Interaction, content: str) -> None:
    if isinstance(source, discord.Interaction):
        if source.response.is_done():
            await source.followup.send(content)
        else:
            await source.response.send_message(content)
    else:
        await source.channel.send(content)


async def _handle_system_info(_source: discord.Message | discord.Interaction) -> str:
    """Handle system info command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The system information.
    """
    return get_system_info()


async def _handle_shutdown(_source: discord.Message | discord.Interaction) -> str:
    """Handle shutdown command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The shutdown message.
    """
    if IS_WINDOWS:
        return ERR_WINDOWS_ONLY.format(action="Shutdown")

    await asyncio.to_thread(subprocess.Popen, ["sudo", "shutdown", "now"])
    return MSG_SHUTDOWN


async def _handle_restart(_source: discord.Message | discord.Interaction) -> str:
    """Handle restart command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The restart message.
    """
    if IS_WINDOWS:
        return ERR_WINDOWS_ONLY.format(action="Restart")

    await asyncio.to_thread(subprocess.Popen, ["sudo", "reboot"])
    return MSG_RESTART


async def _handle_update(source: discord.Message | discord.Interaction) -> str:
    """Handle update command.

    Args:
        source: The Discord message or interaction that triggered the command.

    Returns:
        The update result message.
    """
    if IS_WINDOWS:
        return ERR_WINDOWS_ONLY.format(action="Update via `apt`")

    await respond(source, MSG_UPDATE_START)

    try:
        update_result = await asyncio.to_thread(
            subprocess.run,
            ["sudo", "apt", "update"],
            capture_output=True,
            text=True,
            timeout=APT_UPDATE_TIMEOUT,
        )

        upgrade_result = await asyncio.to_thread(
            subprocess.run,
            ["sudo", "apt", "upgrade", "-y"],
            capture_output=True,
            text=True,
            timeout=APT_UPGRADE_TIMEOUT,
        )

        combined_output = update_result.stdout + "\n" + upgrade_result.stdout
        last_lines = "\n".join(combined_output.strip().splitlines()[-30:])

        return MSG_UPDATE_DONE.format(output=last_lines)

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        return ERR_UPDATE.format(error=e)


async def _handle_disk_usage(_source: discord.Message | discord.Interaction) -> str:
    """Handle disk usage command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The disk usage message.
    """
    try:
        if IS_WINDOWS:
            total, used, free = shutil.disk_usage("/")
            return MSG_DISK_USAGE_WINDOWS.format(
                total=total // (2**30),
                used=used // (2**30),
                free=free // (2**30),
            )

        result = await asyncio.to_thread(
            subprocess.run,
            ["df", "-hT", "--exclude-type=tmpfs", "--exclude-type=devtmpfs"],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.strip().split("\n")

        filtered = [lines[0]]
        for line in lines[1:]:
            if line.startswith("/dev/"):
                filtered.append(line)

        output = "\n".join(filtered)

        return MSG_DISK_USAGE.format(output=output)

    except (subprocess.SubprocessError, OSError, shutil.Error) as e:
        return ERR_DISK_USAGE.format(error=e)


async def _handle_speedtest(source: discord.Message | discord.Interaction) -> str:
    """Handle speedtest command.

    Args:
        source: The Discord message or interaction that triggered the command.

    Returns:
        The speed test results message.
    """
    if not shutil.which("speedtest"):
        return ERR_SPEEDTEST_NOT_INSTALLED

    await respond(source, MSG_SPEEDTEST_START)

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            ["speedtest", "--simple"],
            capture_output=True,
            text=True,
            timeout=SPEEDTEST_TIMEOUT,
        )

        return MSG_SPEEDTEST_RESULTS.format(output=result.stdout)

    except subprocess.TimeoutExpired:
        return ERR_SPEEDTEST_TIMEOUT
    except (subprocess.SubprocessError, OSError) as e:
        return ERR_SPEEDTEST_ERROR.format(error=e)


async def _handle_help(_source: discord.Message | discord.Interaction) -> str:
    """Handle help command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The help message.
    """
    return HELP_MESSAGE


async def _handle_fix_permissions(_source: discord.Message | discord.Interaction) -> str:
    """Handle fix permissions command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The fix permissions result message.
    """
    try:
        import os
        import pwd

        username = pwd.getpwuid(os.getuid()).pw_name
        await asyncio.to_thread(
            subprocess.run,
            [
                "sudo",
                "chown",
                "-R",
                f"{username}:{username}",
                f"/home/{username}",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
        )
        return MSG_FIX_PERMS_DONE
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        return ERR_FIX_PERMS.format(error=e)


async def _handle_restart_avahi(_source: discord.Message | discord.Interaction) -> str:
    """Handle restart avahi-daemon command.

    Args:
        _source: The Discord message or interaction that triggered the command.

    Returns:
        The restart avahi result message.
    """
    try:
        await asyncio.to_thread(
            subprocess.run,
            ["sudo", "systemctl", "restart", "avahi-daemon"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return MSG_RESTART_AVAHI_DONE
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        return ERR_RESTART_AVAHI.format(error=e)


# Command handler mapping
_COMMAND_HANDLERS: dict[
    str,
    Callable[[discord.Message | discord.Interaction], Awaitable[str]],
] = {
    CMD_SYSTEM_INFO: _handle_system_info,
    CMD_SHUTDOWN: _handle_shutdown,
    CMD_RESTART: _handle_restart,
    CMD_REBOOT: _handle_restart,
    CMD_UPDATE: _handle_update,
    CMD_DISK_USAGE: _handle_disk_usage,
    CMD_SPEEDTEST: _handle_speedtest,
    CMD_HELP: _handle_help,
    CMD_FIX_PERMS: _handle_fix_permissions,
    CMD_RESTART_AVAHI: _handle_restart_avahi,
}


async def handle_command(cmd: str, source: discord.Message | discord.Interaction) -> str | None:
    """Handle a bot command and return the response.

    Args:
        cmd: The command string to execute.
        source: The Discord message or interaction that triggered the command.

    Returns:
        The response message, or None if no response is needed.
    """
    handler = _COMMAND_HANDLERS.get(cmd)
    if handler:
        return await handler(source)
    return None
