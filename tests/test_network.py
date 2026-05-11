"""Tests for network module."""

import socket
from unittest.mock import MagicMock, patch

import pytest

from network import get_ip, wait_for_dns


def test_get_ip_success():
    """Test get_ip returns a valid IP address."""
    with patch("socket.socket") as mock_socket:
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.getsockname.return_value = ("192.168.1.100", 12345)

        result = get_ip()

        assert result == "192.168.1.100"
        mock_sock.connect.assert_called_once_with(("8.8.8.8", 80))
        mock_sock.close.assert_called_once()


def test_get_ip_failure():
    """Test get_ip returns 'unknown' on socket error."""
    with patch("socket.socket") as mock_socket:
        mock_socket.side_effect = OSError("Network error")

        result = get_ip()

        assert result == "unknown"


@pytest.mark.asyncio
async def test_wait_for_dns_success():
    """Test wait_for_dns succeeds on first attempt."""
    with patch("socket.gethostbyname") as mock_gethostbyname:
        mock_gethostbyname.return_value = "93.184.216.34"

        await wait_for_dns()

        mock_gethostbyname.assert_called_once_with("discord.com")


@pytest.mark.asyncio
async def test_wait_for_dns_retry():
    """Test wait_for_dns retries on failure."""
    with patch("socket.gethostbyname") as mock_gethostbyname:
        mock_gethostbyname.side_effect = [socket.gaierror("DNS error"), "93.184.216.34"]

        await wait_for_dns(retry_count=2, retry_delay=0)

        assert mock_gethostbyname.call_count == 2


@pytest.mark.asyncio
async def test_wait_for_dns_failure():
    """Test wait_for_dns raises RuntimeError after all retries."""
    with patch("socket.gethostbyname") as mock_gethostbyname:
        mock_gethostbyname.side_effect = socket.gaierror("DNS error")

        with pytest.raises(RuntimeError, match="DNS resolution failed"):
            await wait_for_dns(retry_count=2, retry_delay=0)
