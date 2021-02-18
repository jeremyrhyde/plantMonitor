#!/usr/bin/env python3
"""
This application provides a CLI for the robots
"""

from overseer.Overseer import Overseer
from overseer.overseer_config import *
from overseer.plant_dict import *

from subprocess import Popen, PIPE
from util import Logger
import time
import httplib2
import json
import os


# --------------- Types of manual input ---------------

def user_input(logger):
    print("\nOptions: WATER")

    user_option = input("Enter option: ")

    logger.info("User command input - {}".format(user_option))

    return user_option

def plant_input(logger):

    print("\nPlant options:")

    key_list = []
    i = 0
    for key in plant_dict:
        print('[{}] - {}'.format(i, key))
        key_list.append(key)
        i = i + 1

    plant_option = input("Enter option: ")

    try:
        plant_num = int(plant_option)
    except Exception as e:
        logger.info("Invalid input {}".format(platn_option)
        return 'X'

    logger.info("User plant input - {} [{}]".format(key_list[plant_num], plant_num))
    return plant_num

# ------------- API get and pull requests --------------

def send_api_cmd(api_endpoint, data_key, data_value):
    data = {data_key : data_value}
    data_json = json.dumps(data)

    output = ''

    h = httplib2.Http()
    try:
        resp, content = h.request("http://0.0.0.0:5002/{}/".format(api_endpoint), "POST", data_json, {"content-type":"application/json"})
    except Exception as e:
        print(e)

    #print(content)

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

# --------------------- MAIN LOOP ----------------------

def main():

    time.sleep(3)
    # Logging
    logger = Logger('/home/pi/temp.log')

    # Initialize overseer
    overseer_id = '0'
    overseer_logger = logger.init('OVERSEER', overseer_id)

    overseer_logger.info('---------------------------------')
    overseer_logger.info('--------- PLANT MONITOR ---------')
    overseer_logger.info('---------------------------------')

    overseer_logger.info('OVERSEER INITIALIZATION...')

    overseer = Overseer(overseer_logger)

    overseer_logger.info('Overseer setup complete!')

    # Initialize gardener user
    user_id = "000"
    user_logger = logger.init("USER G", user_id)
    user_logger.info('Overseer user setup complete!')

    overseer_logger.info('OVERSEER INITIALIZATION COMPLETE!')

    # ----------------- API Checks  ----------------

    # Send to api that gardener setup is finished
    send_api_cmd('overseer_ready', 'ready', 'yes')

    # Recieve api signal that robot setup is complete
    get_api_cmd('robot_ready', 'ready', 'yes')

    # --------------- Manual User Loop --------------

    while True:
        user_option = user_input(user_logger).upper()

        if user_option == 'WATER':
            para = plant_input(user_logger)

            if para != 'X':
                overseer.queue_command(user_option, para)
        else:
            overseer.queue_command(user_option)

    # Clean up
    print("Exiting program...")
    logger.close()


if __name__ == "__main__":
    main()
