[Unit]
Description=Robot Program
After=network.target api.service

[Service]
Type=forking
Restart=on-failure
RestartSec=3
ExecStart=/usr/bin/screen -L -dmS robot_screen bash -c 'cd "/home/pi/robot_testing/The_Wireless_Army/" ; /usr/bin/python3 -u "robot_cmdline.py" -f "logs/RAW_UART.log"'
User=pi

[Install]
WantedBy=multi-user.target