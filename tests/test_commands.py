"""Tests for bot.commands module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.commands import handle_command


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

    assert result is not None
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

        assert result is not None
        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_shutdown_linux():
    """Test handle_command shutdown on Linux."""
    with (
        patch("bot.commands.IS_WINDOWS", False),
        patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread,
    ):

        result = await handle_command("shutdown", MagicMock())

        assert result is not None
        assert "Shutting down" in result
        mock_to_thread.assert_called_once()


@pytest.mark.asyncio
async def test_handle_command_restart_windows():
    """Test handle_command restart on Windows."""
    with patch("bot.commands.IS_WINDOWS", True):
        result = await handle_command("restart", MagicMock())

        assert result is not None
        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_restart_linux():
    """Test handle_command restart on Linux."""
    with (
        patch("bot.commands.IS_WINDOWS", False),
        patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread,
    ):

        result = await handle_command("restart", MagicMock())

        assert result is not None
        assert "Restarting" in result
        mock_to_thread.assert_called_once()


@pytest.mark.asyncio
async def test_handle_command_update_windows():
    """Test handle_command update on Windows."""
    with patch("bot.commands.IS_WINDOWS", True):
        result = await handle_command("update", MagicMock())

        assert result is not None
        assert "only available on linux" in result.lower()


@pytest.mark.asyncio
async def test_handle_command_speedtest_not_installed():
    """Test handle_command speedtest when not installed."""
    with patch("shutil.which", return_value=None):
        result = await handle_command("speedtest", MagicMock())

        assert result is not None
        assert "not installed" in result.lower()
