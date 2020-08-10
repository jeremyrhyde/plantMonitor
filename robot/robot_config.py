#!/usr/bin/env python3
"""Robot Config
"""

from .actuators.servo import pulse_map
import socket

DAILY_CSV = "logs/daily_actions.csv"
SCHED_CSV = "logs/scheduled_actions.csv"

DAILY_FMT = "%H:%M:%S.%f"
SCHED_FMT = "%Y-%m-%d %H:%M:%S.%f"
CSV_FMT = "%Y-%m-%d %H:%M:%S"
OLED_FMT = "%m/%d %H:%M - "

TIMEZONE = "America/New_York"

OLED_INTERVAL = 1

# Define cnc
USBSERIAL_CNC = '/dev/ttylACMO' #can switch to auto if needed

X_MIN = 30
X_MAX =  -30
Y_MIN = -1
Y_MAX = 1





print('Hi Boss!')
