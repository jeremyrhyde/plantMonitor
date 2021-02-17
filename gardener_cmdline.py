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
import httplib2
import json


# ---- Types of manual input ----
def user_input(logger):
    print("\nOptions: On / Off / X")

    user_option = input("Enter option: ")

    logger.info("User input - {}".format(user_option))

    return user_option

def send_api_cmd(api_endpoint, data_json):
        h = httplib2.Http()
        try:
            resp, content = h.request("http://0.0.0.0:5002/{}/".format(api_endpoint), "POST", data_json, {"content-type":"application/json"})
        except Exception as e:
            print(e)

        #print(content)

def main():


    # Logging
    logger = Logger('/home/pi/temp.log')
    logger.clear_log_file()

    gardener_id = '0'
    gardener_logger = logger.init('GARDENER', gardener_id)

    gardener_logger.info('----------------------------')
    gardener_logger.info('GARDENER INITIALIZATION...')
    gardener_logger.info('Gardener setup complete!')

    # Initialize gardener user
    user_id = "000"
    user_logger = logger.init("USER G", user_id)
    user_logger.info('Gardener user setup complete!')

    gardener_logger.info('GARDENER INITIALIZATION COMPLETE!')

    # Send to api that gardener setup is finished
    data = {'ready' : 'yes'}
    data_json = json.dumps(data)
    send_api_cmd('robot_ready', data_json)

    # ----- Manual User Loop -------
    while True:
        user_option = user_input(user_logger).upper()

    # Clean up
    print("Exiting program...")
    logger.close()


if __name__ == "__main__":
    main()
