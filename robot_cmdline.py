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


# ---- Types of manual input ----
def user_input(logger):
    print("\nOptions: On / Off / X")

    user_option = input("Enter option: ")

    logger.info("User input - {}".format(user_option))

    return user_option

def main():

    CNC_MOTION = False
    robot_id = '000'
    #config = (Logger.Log_Config.STREAM_LOG | Logger.Log_Config.FILE_LOG)

    # Logging
    logger = Logger('temp.log')
    robot_logger = logger.init('ROBOT', robot_id)
    cnc_logger = logger.init('CNC', robot_id)

    self.logger.info('ROBOT INITIALIZATION...')

    robot = Robot(robot_id, robot_logger, cnc_logger)

    sched = Robot_Scheduler(robot)
    robot.register_scheduler(sched)


    # ----- Manual User Loop -------
    user_id = "000"
    user_logger = logger.init("USER", user_id)

    robot_logger.info('User setup complete!')

    self.logger.info('ROBOT INITIALIZATION COMPLETE!')

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
