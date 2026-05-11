"""Tests for system_info module."""

from unittest.mock import MagicMock, patch

from system_info import get_cpu_temp, get_system_info


def test_get_cpu_temp_linux():
    """Test get_cpu_temp on Linux."""
    mock_file = MagicMock()
    mock_file.read.return_value = "50000"
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_file
    with patch("system_info.IS_WINDOWS", False), patch("builtins.open", return_value=mock_cm):
        result = get_cpu_temp()

        assert result == 50.0


def test_get_cpu_temp_windows():
    """Test get_cpu_temp on Windows returns None."""
    with patch("system_info.IS_WINDOWS", True):
        result = get_cpu_temp()

        assert result is None


def test_get_cpu_temp_file_error():
    """Test get_cpu_temp returns None on file read error."""
    with (
        patch("system_info.IS_WINDOWS", False),
        patch("builtins.open", side_effect=OSError("File not found")),
    ):
        result = get_cpu_temp()

        assert result is None


def test_get_cpu_temp_invalid_value():
    """Test get_cpu_temp returns None on invalid value."""
    mock_file = MagicMock()
    mock_file.read.return_value = "invalid"
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_file
    with patch("system_info.IS_WINDOWS", False), patch("builtins.open", return_value=mock_cm):
        result = get_cpu_temp()

        assert result is None


def test_get_system_info():
    """Test get_system_info returns formatted string."""
    with (
        patch("system_info.get_cpu_temp", return_value=45.5),
        patch("psutil.cpu_percent", return_value=25.0),
        patch("psutil.virtual_memory") as mock_ram,
        patch("psutil.disk_usage") as mock_disk,
        patch("system_info.get_ip", return_value="192.168.1.100"),
    ):

        mock_ram.return_value = MagicMock(used=2 * 1024**3, total=8 * 1024**3, percent=25)
        mock_disk.return_value = MagicMock(used=100 * 1024**3, total=500 * 1024**3, percent=20)

        result = get_system_info()

        assert "45.5°C" in result
        assert "25.0%" in result
        assert "192.168.1.100" in result
        assert "SYSTEM INFO" in result


def test_get_system_info_no_temp():
    """Test get_system_info with no temperature available."""
    with (
        patch("system_info.get_cpu_temp", return_value=None),
        patch("psutil.cpu_percent", return_value=25.0),
        patch("psutil.virtual_memory") as mock_ram,
        patch("psutil.disk_usage") as mock_disk,
        patch("system_info.get_ip", return_value="192.168.1.100"),
    ):

        mock_ram.return_value = MagicMock(used=2 * 1024**3, total=8 * 1024**3, percent=25)
        mock_disk.return_value = MagicMock(used=100 * 1024**3, total=500 * 1024**3, percent=20)

        result = get_system_info()

        assert "N/A" in result
        assert "25.0%" in result
