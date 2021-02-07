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

X_MAX = 3250
Y_MAX = 750

RELAY_PIN_PL = 17
RELAY_PIN_WATER = 22
#RELAY_PIN_CNC = 26
#RELAY_PIN_CNC = 26


STEPPER_X_DIR_PIN = 26
STEPPER_X_STEP_PIN = 26
STEPPER_X_ENABLE_PIN = 26
LIMIT_X_PIN = 26

STEPPER_Y_DIR_PIN = 26
STEPPER_Y_STEP_PIN = 26
STEPPER_Y_ENABLE_PIN = 26
LIMIT_Y_PIN = 26





print('Hi Boss!')
