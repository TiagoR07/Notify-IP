# IP Discord Notifier (Linux / Raspberry Pi)

![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Linux-yellow)
![Systemd](https://img.shields.io/badge/systemd-enabled-green)

A simple Discord bot that helps you keep track of your Raspberry Pi or Linux-based systems on home networks that use DHCP.

Because DHCP may assign a different IP address on each boot, this bot sends the current IP to your Discord account automatically. This makes it much easier to find and connect to the Pi again, especially when Avahi / `raspberrypi.local` is not working reliably.

## Features

- Sends your Raspberry Pi IP address on startup
- Makes it easier to find the Pi after DHCP assigns a new IP
- Supports `shutdown`, `restart`, `system info`, `disk usage`, `speedtest`, `update`, and `restart avahi` commands
- Uses a virtual environment
- Runs automatically on boot with `systemd`

## How it works
- The Raspberry Pi boots
- systemd automatically starts the bot
- The bot retrieves the current local IP
- The IP is sent to your Discord DM
- You can then control the Pi remotely via commands

## Requirements

- Raspberry Pi OS or another Linux system
- Python 3
- Discord bot token
- Discord user ID
- `sudo` access for the commands you want to run

## Project Setup

### 1) Clone the repository

```bash
git clone https://github.com/TiagoR07/Notify-IP.git
cd Notify-IP
```

### 2) Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install discord.py python-dotenv psutil requests
```

### 4) Configure Credentials

Create a .env file:

```bash
nano .env
```

Update the fields with your actual Discord credentials:

```bash
DISCORD_TOKEN=your_bot_token_here
DISCORD_USER_ID=your_user_id_here
```
## Run the bot manually

```bash
source venv/bin/activate
python main.py
```

---

## Run on Boot with systemd

The project includes a `setup.sh` script to automate the creation of the systemd service. Before running, ensure the paths inside `setup.sh` match your username.

### Make it executable

```bash
chmod +x setup.sh
```

### Run it

```bash
./setup.sh
```

---

## Edit the service file if needed

```bash
sudo nano /etc/systemd/system/ip-discord.service
```

---

## Toggle the service on or off

If you need to quickly stop or start the bot, use the included toggle script:

### Make it executable

```bash
chmod +x toggle.sh
```

### Run it

```bash
./toggle.sh
```

---


## Configure sudo permissions

Create a dedicated sudoers file:

```bash
sudo visudo -f /etc/sudoers.d/ip-discord
```

Add these lines, replacing `tiago` with your actual user:

```text
tiago ALL=(ALL) NOPASSWD: /sbin/shutdown
tiago ALL=(ALL) NOPASSWD: /sbin/reboot
tiago ALL=(ALL) NOPASSWD: /usr/bin/apt update, /usr/bin/apt upgrade *, /usr/bin/apt install *
tiago ALL=(ALL) NOPASSWD: /bin/systemctl restart avahi-daemon, /bin/systemctl enable avahi-daemon
```

---
## Security Notice

> [!WARNING]
> ⚠️ **SECURITY NOTICE**
>
> This project provides **remote system control capabilities via Discord**.
>
> ### Capabilities include:
> - System shutdown / reboot  
> - Package management (apt update/upgrade/install)  
> - Service control (systemctl)  
> - System monitoring
>
> ### Requirements:
> - Access restricted to a single trusted Discord user (`DISCORD_USER_ID`)
> - Bot token stored securely in `.env`
> - Must be used only in a private/home network environment
>
> Improper configuration may result in **unauthorized remote control of the system**.

## Notes
- Do not expose your Discord bot token publicly.
- This project is especially useful on home networks that use
DHCP, where the Raspberry Pi may get a different IP after each reboot.
- Avahi / `raspberrypi.local` can be convenient, but it does not always work reliably, so the Discord notification provides a practical fallback.
- Some commands require a Linux based OS because they depend on system tools like systemctl, apt, and /sys hardware interfaces.

## LICENSE
Notify-IP is released under the [MIT License](https://github.com/TiagoR07/Notify-IP/blob/main/LICENSE). 

Feel free to use, modify, and distribute the software as you wish! If you find this tool useful, I’d be truly grateful if you could keep a reference to the original author. It helps support my work and lets others find the project.

Contributions are always welcome! 🚀
