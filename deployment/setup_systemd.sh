#!/bin/bash

# Setup systemd service for automatic restart on reboot
# Alternative to docker-compose for systemd-based systems

set -e

APP_NAME="strategic-insight"
DEPLOY_DIR="/opt/${APP_NAME}"

echo "Creating systemd service for ${APP_NAME}..."

# Create systemd service file
cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Weekly Strategic Insight Engine
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${DEPLOY_DIR}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable ${APP_NAME}.service

# Start service
systemctl start ${APP_NAME}.service

echo "Systemd service installed and started"
echo "Status: systemctl status ${APP_NAME}"
echo "Restart: systemctl restart ${APP_NAME}"
echo "Stop: systemctl stop ${APP_NAME}"
