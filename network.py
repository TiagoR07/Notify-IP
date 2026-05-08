import asyncio
import logging
import socket

logger = logging.getLogger(__name__)

async def wait_for_dns(host: str = "discord.com", retry_count: int = 10, retry_delay: int = 3) -> None:
    for i in range(retry_count):
        try:
            socket.gethostbyname(host)
            return
        except socket.gaierror:
            logger.warning(f"DNS fail attempt {i+1}")
            await asyncio.sleep(retry_delay)
    raise RuntimeError("DNS resolution failed")


def get_ip() -> str:
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ip
    except OSError:
        return "unknown"
    finally:
        if s:
            s.close()