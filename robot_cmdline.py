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

def cnc_motion_input(logger):
    print("\nMotion Options: X 00 / Y 00")

    cnc_option = input("Enter motion option: ")

    logger.info("CNC input - {}".format(cnc_option))

    if cnc_option and cnc_option != 'CNC_MOTION' and cnc_option[0] != 'X' and cnc_option[0] != 'Y':
        logger.warn("Error bad input for cnc motion")
    else:
        return cnc_option

def cnc_feeedrate_input(logger):
    print("\nFeedrate Options: 00")

    cnc_option = input("Enter option: ")

    logger.info("CNC input - {}".format(cnc_option))

    return cnc_option

def main():

    CNC_MOTION = False

    config = (Logger.Log_Config.STREAM_LOG | Logger.Log_Config.FILE_LOG)

    # Logging
    log_file = 'first_logfile.log'
    logger = Logger('ROBOT', '000')
    #logger = Logger()

    # Robot
    robot_id = "000"
    robot_logger = logger.init("ROBOT", robot_id)

    robot = Robot(robot_id, robot_logger)
    sched = Robot_Scheduler(robot)
    robot.register_scheduler(sched)


    # ----- Manual User Loop -------
    user_id = "000"
    user_logger = logger.init("USER", user_id)

    robot_logger.info('User setup complete!')

    while True:
        print(CNC_MOTION)
        if CNC_MOTION:
            cnc_option = cnc_motion_input(user_logger)
            if cnc_option == 'CNC_MOTION':
                CNC_MOTION = not CNC_MOTION
            elif cnc_option:
                #print(user_option, cnc_option)
                robot.queue_command(user_option, cnc_option)

        else:
            user_option = user_input(user_logger).upper()


            if user_option == 'CNC_MOTION':
                CNC_MOTION = not CNC_MOTION

            elif user_option == 'CNC_FEEDRATE':
                cnc_option = cnc_feedrate_input(user_logger)
                robot.queue_command(user_option, cnc_option)
            else:
                robot.queue_command(user_option)
        #else:
        #    robot.queue_command(user_option)

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
