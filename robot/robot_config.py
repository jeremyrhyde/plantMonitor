#!/usr/bin/env python3
"""Robot Config
"""

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

X_MAX =  22
Y_MAX = 106

RELAY_PIN_PL = 17
RELAY_PIN_WATER = 22
RELAY_PIN_CNC = 26





print('Hi Boss!')
