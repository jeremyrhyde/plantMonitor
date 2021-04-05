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

        self.logger.info('Registering schedule...')
        self.register_passive_lighting_schedule()
        self.register_mapping_schedule()
        self.register_watering_schedule()
        self.register_calibration_schedule()
        self.logger.info('Registering schedule complete!')

        self.sched.start()

        # Setting passive lighting state
        self.logger.info('Initial overseer actions...')
        self.passive_lighting_state()

    # Stop threads and close out of all objects
    def close(self):
        self._stop_event.set()
        self.sched.shutdown()
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

    ## ----------------------------- MAIN COMMANDS -----------------------------

    def water_plant(self, plant_key, return_origin = False):

        # Get metadata
        present = plant_dict[plant_key]['present']
        pos_list = plant_dict[plant_key]['position']
        water_amount = plant_dict[plant_key]['water_amount']
        water_schedule = plant_dict[plant_key]['water_schedule']

        if present == 'yes':

            for pos in pos_list.split('|'):

                if '-' in pos:

                    self.logger.info('Watering {} with {} mL from {} [FREQUENCY: {}]'.format(plant_key, water_amount, pos, str(water_schedule)))

                    temp0 = pos.split(',')

                    # Turn on water
                    if '-' in temp0[0] and '-' in temp0[1]:
                        tempx = temp0[0].split('-')
                        tempy = temp0[1].split('-')

                        pos1 = tempx[0] + ',' + tempy[0] + ']'
                        pos2 = str(tempx[0].split('[')[0]) + '[' + tempx[1] + ',' + tempy[1]

                    # Check straight line
                    elif '-' in temp0[0]:
                        tempx = temp0[0].split('-')
                        tempy = temp0[1]

                        pos1 = tempx[0] + ',' + tempy
                        pos2 = str(tempx[0].split('[')[0]) + '[' + tempx[1] + ',' + tempy

                    else:
                        tempx = temp0[0]
                        tempy = temp0[1].split('-')

                        pos1 = tempx + ',' + tempy[0] + ']'
                        pos2 = tempx + ',' + tempy[1]

                        self.logger.info('Moving from {} to {}'.format(pos1, pos2))

                    self.send_robot_command(pos1)
                    self.send_robot_command('ON_W')

                    self.send_robot_command(pos2)
                    self.send_robot_command('OFF_W')

                else:
                    self.logger.info('Watering {} with {} mL at {} [FREQUENCY: {}]'.format(plant_key, water_amount, pos, str(water_schedule)))

                    #Send move command
                    self.send_robot_command(pos)

                    #Send water Command
                    #self.send_robot_command('WATER', water_amount)

            #Return to origin
            if return_origin:
                self.send_robot_command('%[0,50]')
        else:
            self.logger.info('WARNING! Plant is not in plantMonitor bed')


    ## -------------------------- REGISTERING SCHEDULE -------------------------

    # Register calibration schedule
    def register_calibration_schedule(self):
        self.logger.info(' - Setting up calibration schedule...')

        self.sched.add_job(self.calibrate_robot, 'cron', hour = 10, id='Calibration job')

    # Register watering schedule
    def register_passive_lighting_schedule(self):
        self.logger.info(' - Setting up passive lighting schedule...')

        ON_SCHEDULE = PASSIVE_LIGHTING_SCHEDULE[0].split(':')
        OFF_SCHEDULE = PASSIVE_LIGHTING_SCHEDULE[1].split(':')


        self.sched.add_job(self.passive_lighting_robot, 'cron', hour = ON_SCHEDULE[0], minute = ON_SCHEDULE[1], args=[True], id='Turn on passive lighting job')
        self.sched.add_job(self.passive_lighting_robot, 'cron', hour = OFF_SCHEDULE[0], minute = OFF_SCHEDULE[1], args=[False], id='Turn off passive lighting job')


    # Register mapping schedule
    def register_mapping_schedule(self):
        self.logger.info(' - Setting up mapping schedule...')

        for t in range(0, len(MAPPING_SCHEDULE)):
            t_array = MAPPING_SCHEDULE[t].split(':')

            self.sched.add_job(self.mapping_robot, 'cron', hour = t_array[0], minute = t_array[1], id='Turn on mapping job [{}]'.format(t))


    # Register watering schedule
    def register_watering_schedule(self):
        i = 0
        key_list = []
        # most_freq_water = ['month', 1]

        self.logger.info(' - Setting up water schedule...')

        # Add watering schedule
        for plant_key in plant_dict:
            key_list.append(plant_key)
            self.logger.info('     - Scheduling watering of [{}]'.format(key_list[i]))

            interval = plant_dict[plant_key]['water_schedule'][0]
            freq = int(plant_dict[plant_key]['water_schedule'][1])

            if interval == 'month':
                if freq == 1:
                    self.sched.add_job(self.water_plant, 'cron', day = '1'.format(math.ceil(30/freq)), hour = '12', minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
                else:
                    self.sched.add_job(self.water_plant, 'cron', day = '1-31/{}'.format(math.ceil(30/freq)), hour = '12', minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
            elif interval == 'week':
                if freq == 1:
                    self.sched.add_job(self.water_plant, 'cron', day_of_week = '0'.format(math.ceil(6/freq)), hour = '12', minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
                else:
                    self.sched.add_job(self.water_plant, 'cron', day_of_week = '0-6/{}'.format(math.ceil(6/freq)), hour = '12', minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
            elif interval == 'day':
                if freq == 1:
                    self.sched.add_job(self.water_plant, 'cron', hour = '12'.format(math.ceil(11/freq)), minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
                else:
                    self.sched.add_job(self.water_plant, 'cron', hour = '12-23/{}'.format(math.ceil(11/freq)), minute=i, args=[key_list[i], True], id='{} job'.format(key_list[i]))
            else:
                self.logger.info('Error! Bad interval input (day, week, month)')

            # if most_freq_water[0] == 'month':
            #     if interval == 'month':
            #         most_freq_water[1] = max(most_freq_water[1], freq)
            #     elif (interval == 'week' or interval == 'day'):
            #         most_freq_water = [interval, freq]
            # elif most_freq_water[0] == 'week':
            #     if interval == 'week':
            #         most_freq_water[1] = max(most_freq_water[1], freq)
            #     elif (interval == 'day'):
            #         most_freq_water = [interval, freq]
            # elif most_freq_water[0] == 'day':
            #     if interval == 'day':
            #         most_freq_water[1] = max(most_freq_water[1], freq)

            i = i + 1

        # # Add calibration schedule
        # interval = most_freq_water[0]
        # freq = most_freq_water[1]
        #
        # if interval == 'month':
        #     if freq == 1:
        #         self.sched.add_job(self.calibrate_robot, 'cron', day = '1'.format(math.ceil(30/freq)), hour = '12', minute=i, id='Calibration job')
        #     else:
        #         self.sched.add_job(self.calibrate_robot, 'cron', day = '1-31/{}'.format(math.ceil(30/freq)), hour = '12', minute=i, id='Calibration job')
        # elif interval == 'week':
        #     if freq == 1:
        #         self.sched.add_job(self.calibrate_robot, 'cron', day_of_week = '0'.format(math.ceil(6/freq)), hour = '12', minute=i, id='Calibration job')
        #     else:
        #         self.sched.add_job(self.calibrate_robot, 'cron', day_of_week = '0-6/{}'.format(math.ceil(6/freq)), hour = '12', minute=i, id='Calibration job')
        # elif interval == 'day':
        #     if freq == 1:
        #         self.sched.add_job(self.calibrate_robot, 'cron', hour = '12'.format(math.ceil(11/freq)), minute=i, id='Calibration job')
        #     else:
        #         self.sched.add_job(self.calibrate_robot, 'cron', hour = '12-23/{}'.format(math.ceil(11/freq)), minute=i, id='Calibration job')
        # else:
        #     self.logger.info('Error! Bad interval input (day, week, month)')

    def print_schedule(self):
        self.logger.info('Print overseer schedule: ')

        job_list = self.sched.get_jobs()
        for job in job_list:
            self.logger.info(' - {}'.format(job))

    ## --------------------------- COMMANDS TO ROBOT ---------------------------

    def passive_lighting_state(self):

        def time_in_range(start, end, x):
            """Return true if x is in the range [start, end]"""
            if start <= end:
                return start <= x <= end
            else:
                return start <= x or x <= end

        ON_SCHEDULE = PASSIVE_LIGHTING_SCHEDULE[0].split(':')
        OFF_SCHEDULE = PASSIVE_LIGHTING_SCHEDULE[1].split(':')

        now = datetime.datetime.now().time()
        start = datetime.time(int(ON_SCHEDULE[0]), int(ON_SCHEDULE[1]), 0, 0)
        end = datetime.time(int(OFF_SCHEDULE[0]), int(OFF_SCHEDULE[1]), 0, 0)

        self.passive_lighting_robot(time_in_range(start, end, now))


    def mapping_robot(self):
        self.logger.info('Overseer controlled mapping of robot')

        self.send_robot_command('MAP')


    def calibrate_robot(self):
        self.logger.info('Overseer controlled calibration of robot')

        self.send_robot_command('CAL')


    def passive_lighting_robot(self, onoff):
        if onoff:
            self.logger.info('Overseer controlled turning ON passive lighting')
            self.send_robot_command('ON_PL')
        else:
            self.logger.info('Overseer controlled turning OFF passive lighting')
            self.send_robot_command('OFF_PL')


    ## ------------------------------ API COMMANDS -----------------------------

    def send_robot_command(self, command, para = ''):
        data = {'command' : command, 'para' : para}
        #print(str(data))
        data_json = json.dumps(data)

        try:
            resp, content = self.h.request("http://0.0.0.0:5002/command/", "POST", data_json, {"content-type":"application/json"})
        except Exception as e:
            print(e)
