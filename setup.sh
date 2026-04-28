#!/bin/bash

# Path to your Python script
SCRIPT_PATH="/home/pi/notify_ip.py"
PYTHON_PATH="/usr/bin/python3"
SERVICE_NAME="ip-discord.service"

# Check if the Python script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found at $SCRIPT_PATH"
    exit 1
fi

# Create the systemd service file
echo "Creating systemd service file..."

cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null
[Unit]
Description=Send Pi IP to Discord
After=network-online.target
Wants=network-online.target
DefaultDependencies=no
Before=display-manager.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/tiago/Notify-ip/main.py
WorkingDirectory=/home/tiago/Notify-ip
Environment="PYTHONUNBUFFERED=1"
StandardOutput=journal
Restart=on-failure
User=tiago

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Setup complete. The service has been enabled and started."