#!/usr/bin/env python3
"""
This application provides a CLI for the robots
"""

from robot import Robot_Scheduler
from robot.Robot import Robot
from robot.robot_config import *

from subprocess import Popen, PIPE
from util import Logger
import time
import json
import httplib2


# --------------- Types of manual input ---------------

def user_input(logger):
    print("\nOptions: On / Off / X")

    user_option = input("Enter option: ").upper()

    logger.info("User command input - {}".format(user_option))

    return user_option

def water_input(logger):
    user_option = input("\nEnter amount of water (in mL): ")

    logger.info("User water amount input - {}".format(user_option))

    return user_option

# ------------- API get and pull requests --------------

def get_api_cmd(api_endpoint, json_key, json_filter):
    output = ''

    h = httplib2.Http()

    while(output != json_filter):
        # Retrieve command values
        resp, content = h.request("http://0.0.0.0:5002/{}/".format(api_endpoint), "GET")
        output = json.loads(content.decode("utf-8"))[json_key]
        #print(output)

        time.sleep(1)

    return output

def send_api_cmd(api_endpoint, data_key, data_value):
    data = {data_key : data_value}
    data_json = json.dumps(data)

    output = ''

    h = httplib2.Http()

    try:
        resp, content = h.request("http://0.0.0.0:5002/{}/".format(api_endpoint), "POST", data_json, {"content-type":"application/json"})
    except Exception as e:
        print(e)


# --------------------- MAIN LOOP ----------------------

def main():

    # ----------------- API Checks (P1)  ---------------

    # Wait until Gardener is finish initializing
    get_api_cmd('overseer_ready', 'ready', 'yes')

    # ----------------- Initializing  ------------------

    # Logging
    logger = Logger('/home/pi/temp.log')

    robot_id = '0000'
    robot_logger = logger.init('ROBOT', robot_id)

    cnc_id = '000000'
    cnc_logger = logger.init('CNC', cnc_id)

    robot_logger.info('---------------------------------')
    robot_logger.info('ROBOT INITIALIZATION...')

    # Initialize robot
    robot = Robot(robot_id, robot_logger, cnc_logger)
    sched = Robot_Scheduler(robot)
    robot.register_scheduler(sched)

    # Initialize robot user
    user_id = "000"
    user_logger = logger.init("USER R", user_id)
    user_logger.info('Robot user setup complete!')

    robot_logger.info('ROBOT INITIALIZATION COMPLETE!')
    robot_logger.info('---------------------------------')

    # ----------------- API Checks (P2)  --------------

    # Send to api that gardener setup is finished
    send_api_cmd('robot_ready', 'ready', 'yes')

    # --------------- Manual User Loop ----------------
    while True:

        user_option = user_input(user_logger)

        if user_option == 'WATER':
            para = water_input(user_logger)
            robot.queue_command(user_option, para)

        elif len(user_option) > 0:
            robot.queue_command(user_option)

        if user_option == 'X':
            break

    # --------------------- Close -------------------

    # Clean up
    overseer_logger.info('---------------------------------')
    robot_logger.info('ROBOT CLOSEOUT')
    overseer_logger.info('---------------------------------')

    print("Exiting program...")

    logger.close()
    sched.close()
    robot.close()


if __name__ == "__main__":
    main()
