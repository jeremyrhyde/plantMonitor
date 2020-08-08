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

# Define Servo Pins
DAJ = 15
ARM = 13
RAIL = 12
THUMB = 14
LEVER = 8
NUM_PAD = 11

# Define time parameters for servos
MOVE_TIME = 0.3
PAUSE_TIME = 1.4

# Define sensor pins
RELAY_PIN = 20
SENSOR_PIN = 20
LED_PIN = 21

# BATTERY
SHUNT_OHMS=0.1
MAX_EXPECTED_AMPS=0.75

# Define position of digits on lens
NUM_PAD_CAL1 = 164
NUM_PAD_CAL2 = 93
NUM_POS = {"N1": pulse_map(NUM_PAD_CAL1),                                                     #  check calibration
           "N2": pulse_map(NUM_PAD_CAL1-18),
           "N3": pulse_map(NUM_PAD_CAL1-29),
           "N4": pulse_map(NUM_PAD_CAL1-45),
           "N5": pulse_map(NUM_PAD_CAL1-60),
           "N6": pulse_map(NUM_PAD_CAL2),
           "N7": pulse_map(NUM_PAD_CAL2-13),
           "N8": pulse_map(NUM_PAD_CAL2-13*2),
           "N9": pulse_map(NUM_PAD_CAL2-13*3),
           "N0": pulse_map(NUM_PAD_CAL2-13*4),
           "NN": pulse_map(15)
           }


# Define arm positions           # ARM POSITIONS NEEDS A LOT OF CALIBRATION
NEUTRAL = pulse_map(90)
FALSE_NFC = pulse_map(0)
TAP = pulse_map(90)
NFC = pulse_map(180)

VOLTAGE_LOGGING = False
BLE_ON_OFF = True
API_YES_NO = True

# Define lever positions
LEVER_DOWN = pulse_map(70)
LEVER_NEUTRAL = pulse_map(0)

# Define DAJ positions
DAJ_OPEN = pulse_map(45)
DAJ_CLOSED = pulse_map(0)

# Define thumb lock positions (RIGHTHANDED and LEFTHANDED)
R_LOCK = pulse_map(0)
R_UNLOCK = pulse_map(90)

L_LOCK = pulse_map(0)
L_UNLOCK = pulse_map(100)
#IS_LOCKED = True

# Define doorcode values
USER_DOOR_CODE = False
DEFAULT_DOOR_CODE = [6,6,6,6,6,6,6]

# Define robot based on hostname
host = socket.gethostname()


print('Hi Boss!')
