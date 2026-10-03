[Unit]
Description=Amnezia VPN Shop Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/amnezia-vpn-bot
EnvironmentFile=/opt/amnezia-vpn-bot/.env
ExecStart=/opt/amnezia-vpn-bot/venv/bin/python /opt/amnezia-vpn-bot/main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/amnezia-vpn-bot.log
StandardError=append:/var/log/amnezia-vpn-bot.log

[Install]
WantedBy=multi-user.target