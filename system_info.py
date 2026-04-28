import psutil
from config import IS_WINDOWS
from network import get_ip


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