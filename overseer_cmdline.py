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
import os


# --------------- Types of manual input ---------------

def user_input(logger):
    print("\nOptions: On / Off / X")

    user_option = input("Enter option: ")

    logger.info("User input - {}".format(user_option))

    return user_option

def plant_input(logger):
    print("\nOptions: \n")

    plant_option = input("Enter option: ")

    logger.info("User input - {}".format(plant_option))

    return plant_option

# ------------- API get and pull requests --------------

def send_api_cmd(api_endpoint, data_json):
        h = httplib2.Http()
        try:
            resp, content = h.request("http://0.0.0.0:5002/{}/".format(api_endpoint), "POST", data_json, {"content-type":"application/json"})
        except Exception as e:
            print(e)

        #print(content)

# --------------------- MAIN LOOP ----------------------

def main():

    # Logging
    logger = Logger('/home/pi/temp.log')

    # Initialize overseer
    overseer_id = '0'
    overseer_logger = logger.init('OVERSEER', overseer_id)

    overseer_logger.info('---------------------------------')
    overseer_logger.info('--------- PLANT MONITOR ---------')
    overseer_logger.info('---------------------------------')

    overseer_logger.info('GARDENER INITIALIZATION...')

    overseer = Overseer(overseer_logger)

    overseer_logger.info('Gardener setup complete!')

    # Initialize gardener user
    user_id = "000"
    user_logger = logger.init("USER G", user_id)
    user_logger.info('Gardener user setup complete!')

    overseer_logger.info('GARDENER INITIALIZATION COMPLETE!')

    # ----------------- API Checks  ----------------

    # Send to api that gardener setup is finished
    data = {'ready' : 'yes'}
    data_json = json.dumps(data)
    send_api_cmd('robot_ready', data_json)

    # Recieve api signal that robot setup is complete
    ##
    ##
    ##

    # --------------- Manual User Loop --------------

    while True:
        user_option = user_input(user_logger).upper()

        if user_option == 'WATER':
            para = plant_option(user_logger)

        overseer.queue_command(user_option, para)

    # Clean up
    print("Exiting program...")
    logger.close()


if __name__ == "__main__":
    main()
