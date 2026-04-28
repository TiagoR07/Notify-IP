import asyncio
import socket

async def wait_for_dns(host="discord.com"):
    for i in range(10):
        try:
            socket.gethostbyname(host)
            return
        except socket.gaierror:
            print(f"DNS fail attempt {i+1}")
            await asyncio.sleep(3)
    raise RuntimeError("DNS resolution failed")


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unknown"