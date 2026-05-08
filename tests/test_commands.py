"""Tests for bot.commands module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.commands import handle_command, _send_intermediate


@pytest.mark.asyncio
async def test_send_intermediate_message():
    """Test _send_intermediate with a Message object."""
    source = MagicMock()
    source.channel = AsyncMock()

    await _send_intermediate(source, "test message")

    source.channel.send.assert_called_once_with("test message")


@pytest.mark.asyncio
async def test_send_intermediate_interaction():
    """Test _send_intermediate with an Interaction object."""
    source = MagicMock(spec=[])  # No default attributes
    source.followup = AsyncMock()
    source.followup.send = AsyncMock()

    await _send_intermediate(source, "test message")

    source.followup.send.assert_called_once_with("test message")


@pytest.mark.asyncio
async def test_handle_command_system_info():
    """Test handle_command with 'system info' command."""
    with patch("bot.commands.get_system_info", return_value="System info"):
        result = await handle_command("system info", MagicMock())

        assert result == "System info"


@pytest.mark.asyncio
async def test_handle_command_help():
    """Test handle_command with 'help' command."""
    result = await handle_command("help", MagicMock())

    assert "system info" in result.lower()
    assert "shutdown" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_unknown():
    """Test handle_command with unknown command."""
    result = await handle_command("unknown", MagicMock())

    assert result is None


@pytest.mark.asyncio
async def test_handle_command_shutdown_windows():
    """Test handle_command shutdown on Windows."""
    with patch("bot.commands.IS_WINDOWS", True):
        result = await handle_command("shutdown", MagicMock())

        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_shutdown_linux():
    """Test handle_command shutdown on Linux."""
    with patch("bot.commands.IS_WINDOWS", False), \
         patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        result = await handle_command("shutdown", MagicMock())

        assert "Shutting down" in result
        mock_to_thread.assert_called_once()


@pytest.mark.asyncio
async def test_handle_command_restart_windows():
    """Test handle_command restart on Windows."""
    with patch("bot.commands.IS_WINDOWS", True):
        result = await handle_command("restart", MagicMock())

        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_restart_linux():
    """Test handle_command restart on Linux."""
    with patch("bot.commands.IS_WINDOWS", False), \
         patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        result = await handle_command("restart", MagicMock())

        assert "Restarting" in result
        mock_to_thread.assert_called_once()


@pytest.mark.asyncio
async def test_handle_command_update_windows():
    """Test handle_command update on Windows."""
    with patch("bot.commands.IS_WINDOWS", True):
        result = await handle_command("update", MagicMock())

        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_speedtest_not_installed():
    """Test handle_command speedtest when not installed."""
    with patch("shutil.which", return_value=None):
        result = await handle_command("speedtest", MagicMock())

        assert "not installed" in result.lower()