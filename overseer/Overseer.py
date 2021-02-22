#!/usr/bin/env python3

import socket
import time
import csv
import os
import sys
import json
import math
import datetime
import threading
import httplib2

from os import path
from queue import *
from subprocess import check_output, Popen, PIPE

from .overseer_config import *
from .plant_dict import *

from apscheduler.schedulers.background import BackgroundScheduler

class Overseer:

    h = httplib2.Http()

    plant_name = ''


    COMMANDS = {
        "WATER" : lambda self: self.water_plant(self.plant_name, True),
        "SCH" : lambda self: self.print_schedule(),
        "CAL" : lambda self: self.calibrate_robot(),
    }


    def __init__(self, logger):
        self.logger = logger

        self.plant_dict = plant_dict

        self._q = Queue()
        self._stop_event = threading.Event()

        # Begin robot thread for handling motion and robot logs
        self.logger.info('Starting up overseer thread')
        self.overseer_thread = threading.Thread(target=self._overseer_run)
        self.overseer_thread.start()

        # Setting up schedule
        self.sched = BackgroundScheduler(daemon=True)
        self.register_schedule()
        self.sched.start()

    # Stop threads and close out of all objects
    def close(self):
        self._stop_event.set()

        self.overseer_thread.join()

    def _overseer_run(self):
        while not self._stop_event.is_set():
            command = self._q.get()
            self.command(command)
            self._q.task_done()

    def command(self, command):
        for key, value in self.COMMANDS.items():
            if key == command:
                value(self)
                break

    # Queue a command under the threaded function
    def queue_command(self, command, para = ''):

        if command == 'WATER':
            print('para: ' + para)
            self.plant_name = para

        self._q.put(command)

    def register_schedule(self):

        self.logger.info('Registering schedule...')

        i = 0
        key_list = []
        most_freq_water = ('month', 1)

        for plant_key in plant_dict:
            key_list.append(plant_key)
            self.logger.info(' - Scheduling watering of [{}]'.format(key_list[i]))

            interval = plant_dict[plant_key]['water_schedule'][0]
            freq = int(plant_dict[plant_key]['water_schedule'][1])

            if interval == 'month':
                self.sched.add_job(self.water_plant, 'cron', day = '1-31/{}'.format(math.ceil(30/freq)), hour = '12', minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), args=[key_list[i]], id='{} job'.format(key_list[i]))
            elif interval == 'week':
                self.sched.add_job(self.water_plant, 'cron', day_of_week = '0-6/{}'.format(math.ceil(6/freq)), hour = '12', minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), args=[key_list[i]], id='{} job'.format(key_list[i]))
            elif interval == 'day':
                self.sched.add_job(self.water_plant, 'cron', hour = '12-23/{}'.format(math.ceil(11/freq)), minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), args=[key_list[i]], id='{} job'.format(key_list[i]))
            else:
                self.logger.info('Error! Bad interval input (day, week, month)')

            if most_freq_water[0] == 'month':
                if interval == 'month':
                    most_freq_water[1] = max(most_freq_water[1], freq)
                elif (interval == 'week' or interval == 'day'):
                    most_freq_water[1] = freq
            elif most_freq_water[0] == 'week':
                if interval == 'week':
                    most_freq_water[1] = max(most_freq_water[1], freq)
                elif (interval == 'day'):
                    most_freq_water[1] = freq
            elif most_freq_water[0] == 'day':
                if interval == 'day':
                    most_freq_water[1] = max(most_freq_water[1], freq)

            i = i + 1

        interval = most_freq_water[0]
        freq = most_freq_water[1]

        if interval == 'month':
            self.sched.add_job(self.calibrate_robot, 'cron', day = '1-31/{}'.format(math.ceil(30/freq)), hour = '12', minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), id='{} job'.format(key_list[i]))
        elif interval == 'week':
            self.sched.add_job(self.calibrate_robot, 'cron', day_of_week = '0-6/{}'.format(math.ceil(6/freq)), hour = '12', minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), id='{} job'.format(key_list[i]))
        elif interval == 'day':
            self.sched.add_job(self.calibrate_robot, 'cron', hour = '12-23/{}'.format(math.ceil(11/freq)), minute='{}'.format(int(i/12)), second='{}'.format((i%12)*5), id='{} job'.format(key_list[i]))
        else:
            self.logger.info('Error! Bad interval input (day, week, month)')
            break

        self.logger.info('Registering schedule complete!')

    def print_schedule(self):
        self.logger.info('Print overseer schedule')

        self.sched.print_jobs()

    # def water_schedule(self, plant_key):
    #     present = plant_dict[plant_key]['present']
    #     pos = plant_dict[plant_key]['position']
    #     water_amount = plant_dict[plant_key]['water_amount']
    #     water_schedule = plant_dict[plant_key]['water_schedule']
    #
    #     self.logger.info('Watering {} - at positon: {}, water_amount: {}, frequency: {}'.format(plant_key, pos, water_amount, str(water_schedule)))

    def calibrate_robot(self):

        self.logger.info('Overseer controlled calibration of robot')

        self.send_robot_command('CAL')


    def water_plant(self, plant_key, return_origin = False):

        # Get metadata
        present = plant_dict[plant_key]['present']
        pos = plant_dict[plant_key]['position']
        water_amount = plant_dict[plant_key]['water_amount']
        water_schedule = plant_dict[plant_key]['water_schedule']

        self.logger.info('Watering {} with {} mL of water at positon {} [FREQUENCY: {}]'.format(plant_key, water_amount, pos, str(water_schedule)))

        if present == 'yes':
            #Send move command
            self.send_robot_command(pos)

            #Send water Command
            self.send_robot_command('WATER', water_amount)

            #Return to origin
            if return_origin:
                self.send_robot_command('%[0,50]')
        else:
            self.logger.info('WARNING! Plant is not in plantMonitor bed')


    def send_robot_command(self, command, para = ''):
        data = {'command' : command, 'para' : para}
        print(str(data))
        data_json = json.dumps(data)

        try:
            resp, content = self.h.request("http://0.0.0.0:5002/command/", "POST", data_json, {"content-type":"application/json"})
        except Exception as e:
            print(e)
