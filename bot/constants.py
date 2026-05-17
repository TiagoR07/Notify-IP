"""Constants for bot commands."""

# Command names
CMD_SYSTEM_INFO = "system info"
CMD_SHUTDOWN = "shutdown"
CMD_RESTART = "restart"
CMD_REBOOT = "reboot"
CMD_UPDATE = "update"
CMD_DISK_USAGE = "disk usage"
CMD_SPEEDTEST = "speedtest"
CMD_HELP = "help"
CMD_FIX_PERMS = "fix_permissions"
CMD_RESTART_AVAHI = "restart avahi"

# Command aliases
CMD_RESTART_ALIASES = {CMD_RESTART, CMD_REBOOT}

# Help message
HELP_MESSAGE = (
    "Here are the commands you can use:\n"
    "`system info`: Get system information.\n"
    "`disk usage`: Show disk usage.\n"
    "`speedtest`: Run an internet speed test.\n"
    "`update`: Update the system packages.\n"
    "`shutdown`: Shut down the Raspberry Pi.\n"
    "`restart`: Restart the Raspberry Pi.\n"
    "`fix_permissions`: Recursively restore ownership of /home/tiago.\n"
    "`restart avahi`: Restart the avahi-daemon service.\n"
)

# Error messages
ERR_WINDOWS_ONLY = "❌ {action} is only available on Linux / Raspberry Pi."
ERR_SPEEDTEST_NOT_INSTALLED = (
    "❌ `speedtest-cli` is not installed on this machine.\n"
    "Install it with: `sudo apt install speedtest-cli`"
)
ERR_SPEEDTEST_TIMEOUT = "❌ Speed test timed out after 3 minutes. Try again later."
ERR_DISK_USAGE = "❌ Could not get disk usage: {error}"
ERR_UPDATE = "❌ Error while updating: {error}"
ERR_SPEEDTEST_ERROR = "❌ Error while running speed test: {error}"
ERR_NOT_AUTHORIZED = "❌ Not authorized."
ERR_FIX_PERMS = "❌ Error while fixing permissions: {error}"
ERR_RESTART_AVAHI = "❌ Error while restarting avahi-daemon: {error}"

# Success messages
MSG_SHUTDOWN = "🛑 Shutting down the Raspberry Pi..."
MSG_RESTART = "🔄 Restarting the Raspberry Pi..."
MSG_UPDATE_START = (
    "🔄 Running `sudo apt update && sudo apt upgrade -y`...\n" "This might take a while ⏳"
)
MSG_SPEEDTEST_START = "📡 Running speed test... This might take a while ⏳"
MSG_UPDATE_DONE = "✅ Update finished:\n```{output}```"
MSG_SPEEDTEST_RESULTS = "📡 Speed Test Results:\n```{output}```"
MSG_DISK_USAGE = "💽 Disk Usage:\n```{output}```"
MSG_DISK_USAGE_WINDOWS = (
    "💽 Disk Usage:\n" "Total: {total} GB\n" "Used: {used} GB\n" "Free: {free} GB"
)
MSG_FIX_PERMS_DONE = "✅ Ownership restored for /home/tiago"
MSG_RESTART_AVAHI_DONE = "✅ avahi-daemon restarted successfully"

# Logging messages
LOG_UNAUTHORIZED_SLASH = "⚠️ [{timestamp}] UNAUTHORIZED: User '{user}' (ID: {user_id}) attempted command: /{command}"
LOG_AUTHORIZED_SLASH = "✅ [{timestamp}] User '{user}' (ID: {user_id}) executed command: /{command}"
LOG_UNAUTHORIZED_PREFIX = "⚠️ [{timestamp}] UNAUTHORIZED: User '{user}' (ID: {user_id}) attempted command: !{command}"
LOG_AUTHORIZED_PREFIX = "✅ [{timestamp}] User '{user}' (ID: {user_id}) executed command: !{command}"
