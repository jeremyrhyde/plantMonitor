#!/usr/bin/env python3
"""
This application provides a CLI for the robots
"""

from docopt import docopt
from robot import Robot_Scheduler
from robot.Robot import Robot
from robot.robot_config import *
from subprocess import Popen, PIPE
from util import Logger
import time


# ---- Types of manual input ----
def user_input(logger):
    print("\nOptions: N / T / L / U / D / F / B / X")

    user_option = input("Enter option: ")

    logger.info("User input - {}".format(user_option))

    return user_option

def main():

    config = (Logger.Log_Config.STREAM_LOG | Logger.Log_Config.FILE_LOG)

    # Logging
    logger = Logger()

    # Robot
    robot_id = "000"
    robot_logger = logger.init("ROBOT", robot_id, config)

    my_robot = Robot(robot_id, robot_logger)
    sched = Robot_Scheduler(my_robot)
    my_robot.register_scheduler(sched)


    # ----- Manual User Loop -------
    user_id = "000"
    user_logger = logger.init("USER", user_id)
    user_option = ""

    robot_logger.info('User setup complete!')

    while user_option != "X":
        user_option = user_input(user_logger)

        my_robot.queue_command(user_option)

        time.sleep(2)

    # Clean up
    print("Exiting program...")
    logger.close()

    if log_file:
        log_uart.close()
    if serial_port or serial_file:
        uart.close()

    sched.close()
    my_robot.close()


if __name__ == "__main__":
    #main(args)
    main()
