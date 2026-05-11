import asyncio
import logging
import socket

logger = logging.getLogger(__name__)


async def wait_for_dns(
    host: str = "discord.com", retry_count: int = 10, retry_delay: int = 3
) -> None:
    """Wait for DNS resolution to succeed before proceeding.

    Args:
        host: The hostname to resolve. Defaults to "discord.com".
        retry_count: Number of retry attempts. Defaults to 10.
        retry_delay: Delay between retries in seconds. Defaults to 3.

    Raises:
        RuntimeError: If DNS resolution fails after all retries.
    """
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

        ip: str = str(s.getsockname()[0])
        return ip

    except OSError:
        return "unknown"

    finally:
        if s is not None:
            s.close()
