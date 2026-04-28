#!/bin/bash

# Service name
SERVICE_NAME="ip-discord.service"

# Check if the service is active
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "$SERVICE_NAME is running. Disabling and stopping the service..."
    sudo systemctl disable "$SERVICE_NAME"
    sudo systemctl stop "$SERVICE_NAME"
else
    echo "$SERVICE_NAME is not running. Enabling and starting the service..."
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
fi