#!/bin/bash

# Auto-detect paths
PROJECT_DIR="$(pwd)"
SCRIPT_PATH="$PROJECT_DIR/main.py"
VENV_PATH="$PROJECT_DIR/venv"
SERVICE_NAME="ip-discord.service"
USER_NAME="$(whoami)"

# Check files
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found at $SCRIPT_PATH"
    exit 1
fi

if [ ! -f "$VENV_PATH/bin/python" ]; then
    echo "Error: venv not found at $VENV_PATH"
    exit 1
fi

echo "Creating systemd service file..."

cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null
[Unit]
Description=Send Pi IP to Discord
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PATH/bin/python $SCRIPT_PATH
Restart=on-failure
Environment="PYTHONUNBUFFERED=1"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "Setup complete."