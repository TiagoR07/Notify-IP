import psutil
from config import IS_WINDOWS
from network import get_ip


def get_cpu_temp() -> float | None:
    """Get the current CPU temperature.

    Returns:
        CPU temperature in Celsius, or None if unavailable (e.g., on Windows).
    """
    if IS_WINDOWS:
        return None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read()) / 1000
    except (OSError, ValueError, IOError):
        return None


def get_system_info() -> str:
    """Get formatted system information.

    Returns:
        A formatted string containing CPU temperature, CPU load, RAM usage,
        disk usage, and IP address.
    """
    temp = get_cpu_temp()
    cpu_percent = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    ip = get_ip()

    temp_str = f"{temp:.1f}°C" if temp else "N/A"
    ram_used = f"{ram.used // (1024**2)} MB"
    ram_total = f"{ram.total // (1024**2)} MB"
    disk_used = f"{disk.used // (1024**3)} GB"
    disk_total = f"{disk.total // (1024**3)} GB"

    return (
        "```\n"
        "📊 SYSTEM INFO 📊\n"
        "─────────────────────\n"
        f"🌡️  CPU Temp:  {temp_str:<12}\n"
        f"⚙️  CPU Load:  {cpu_percent:>6.1f}%\n"
        f"🧠 RAM:      {ram_used} / {ram_total} ({ram.percent}%)\n"
        f"💾 Disk:     {disk_used} / {disk_total} ({disk.percent}%)\n"
        f"🌐 IP:       {ip}\n"
        "─────────────────────\n```"
    )