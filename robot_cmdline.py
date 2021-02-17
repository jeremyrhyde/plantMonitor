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


# ---- Types of manual input ----
def user_input(logger):
    print("\nOptions: On / Off / X")

    user_option = input("Enter option: ")

    logger.info("User input - {}".format(user_option))

    return user_option

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

def main():

    robot_id = '0000'
    cnc_id = '000000'

    # Logging
    logger = Logger('temp.log')
    robot_logger = logger.init('ROBOT', robot_id)
    cnc_logger = logger.init('CNC', cnc_id)

    # Wait until Gardener is finish initializing
    get_api_cmd('robot_ready', 'ready', 'yes')

    robot_logger.logger.info('----------------------------')
    robot_logger.logger.info('ROBOT INITIALIZATION...')

    # Initialize robot
    robot = Robot(robot_id, robot_logger, cnc_logger)
    sched = Robot_Scheduler(robot)
    robot.register_scheduler(sched)

    # Initialize robot user
    user_id = "000"
    user_logger = logger.init("USER R", user_id)

    user_logger.info('Robot user setup complete!')
    robot_logger.logger.info('ROBOT INITIALIZATION COMPLETE!')
    robot_logger.logger.info('----------------------------')

    # ----- Manual User Loop -------
    while True:

        user_option = user_input(user_logger).upper()

        if len(user_option) > 0:
            robot.queue_command(user_option)

        if user_option == 'X':
            break

    # Clean up
    print("Exiting program...")
    logger.close()

    # if log_file:
    #     log_uart.close()
    # if serial_port or serial_file:
    #     uart.close()

    sched.close()
    robot.close()


if __name__ == "__main__":
    main()
