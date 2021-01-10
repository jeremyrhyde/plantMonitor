#!/usr/bin/env python3
"""Provides an interface for robots

Robot is a super class of possible robots.
The class should contain functions for each possible robot action.
"""

import socket
import time
import csv
import os
import sys
import json
import datetime
import threading
import httplib2

from os import path
from queue import *
from subprocess import check_output, Popen, PIPE

from .robot_config import *

#Subcomponents
from .actuators import GRBL_Stream
#from .display/gui import *
from .passiveLighting import *
#from .activeLighting import *
from .piCamera import *
#from .sensors import Lock_Sensor, Relay_Sensor, Battery_Sensor

class Robot:

    sched = None

    h = httplib2.Http()

    cnc_direction = ''
    cnc_dist = ''
    cnc_feedrate = ''

    COMMANDS = {
        "TAKE_IMAGE" : lambda self: self.takeCameraImage(),
        "PREVIEW_IMAGE" : lambda self: self.previewImage(),
        "ON" : lambda self: self.passiveLightingOnOff(True),
        "OFF" : lambda self: self.passiveLightingOnOff(),
        #"TurnOnActiveLights" : lambda self: self.activeLightingOnOff(True),
        #"TurnOffActiveLights" : lambda self: self.activeLightingOnOff(),
        "CNC_MOTION" : lambda self: self.move_cnc(self.cnc_direction, self.cnc_dist),
        "CNC_FEEDRATE" : lambda self: self.set_feedrate_cnc(self.cnc_feedrate),
        "X" : lambda self: self.close(),
        #watering
    }

    # --------------------------------------------------------------------------
    # ----------------------------- INITALIZATION ------------------------------
    # --------------------------------------------------------------------------

    def __init__(self, robot_id, logger):
        self.robot_id = robot_id
        self.logger = logger

        #  ----- Initalize threading: Robot, API Interface ------
        self._q = Queue()
        self._stop_event = threading.Event()

        # Begin robot thread for handling motion and robot logs
        self.robot_thread = threading.Thread(target=self._robot_run)
        self.robot_thread.start()

        # Initialize components
        self.passive_led = PassiveLEDs()

        self.camera = Camera()

        self.curr_camera_pos = [0,0]
        #self.cnc = GRBL_Stream()

        self.cnc_feedrate = 100#str(self.cnc.get_feedrate())

        # Begin API
        self.api_interface = threading.Thread(target=self._api_interface)
        self.api_interface.start()

        self.logger.info('Robot setup complete!')

    # Stop threads and close out of all objects
    def close(self):

        self.cnc.close()
        self.passive_led.close()
        self.camera.close()
        self.api_interface.join() # Stop api thread

        self._stop_event.set()



    # Define scheduler
    def register_scheduler(self, sched):
        self.sched = sched

    # Get the robot_id
    def get_robot_id(self):
        return self.robot_id

    # --------------------------------------------------------------------------
    # -------------------------- THREADED FUNCTIONS ----------------------------
    # --------------------------------------------------------------------------

    # This is the thread run function
    def _robot_run(self):
        while not self._stop_event.is_set():
            command = self._q.get()
            self.command(command)
            self._q.task_done()

    # Thread for monitoring api interface
    def _api_interface(self):

        self.logger.info('Connecting to API...')

        while(True):

            # Retrieve command values
            resp, content = self.h.request("http://0.0.0.0:5002/command/", "GET")
            command = json.loads(content.decode("utf-8"))

            if command['command'] != '':
                self.queue_command(command['command'], command['para'])
                self.logger.info(str(command))
            time.sleep(1)


    # --------------------------------------------------------------------------
    # ------------------------ COMMAND & QUEUE FUNCTIONS -----------------------
    # --------------------------------------------------------------------------
    # Run the commmand immediately
    def command(self, command):
        for key, value in self.COMMANDS.items():
            if key == command:
                value(self)
                break

    # Queue a command under the threaded function
    def queue_command(self, command, para = ''):
        if command == 'CNC_MOTION':
            self.cnc_direction = para[0]
            self.cnc_dist = para[2:]

        if command == 'CNC_FEEDRATE':
            self.cnc_feedrate = para

        self._q.put(command)

    # Adds api input to schedule csv
    def add_command_to_schedule(self, date, command):

        #new_scheduled_time = date.strftime(SCHED_FMT)
        with open(SCHED_CSV, 'w+') as schedule_file:
            scheduler = csv.writer(schedule_file)#, delimiter=',')
            scheduler.writerow([date, command])

    # --------------------------------------------------------------------------
    # ------------------------------ MAIN ACTIONS ------------------------------
    # --------------------------------------------------------------------------


    # --------------------------------- CAMERA ---------------------------------

    # Take image
    def takeCameraImage(self):
        self.camera.capture('foo.jpg')
        self.logger.info('Image captured from picamera')

    # View preview for 5 seconds
    def previewImage(self):
        self.camera.preview_5s()
        self.logger.info('Previewing Image from picamera')


    # ---------------------------- PASSIVE LIGHTING ----------------------------

    def passiveLightingOnOff(self, on = False):
        if on:
            self.passive_led.turn_on()
            self.logger.info('Turning on Passive Lighting')
        else:
            self.passive_led.turn_off()
            self.logger.info('Turning off Passive Lighting')


    # ----------------------------- ACTIVE LIGHTING ----------------------------

    # def activeLightingOnOff(self, on = False):
    #     self.logger.info('Active Lighting On / Off')
    #
    # def activeLightingColor(self):
    #     self.logger.info('Active Lighting Color')


    # ----------------------------------- CNC ----------------------------------

    def move_cnc(self, cnc_direction, cnc_dist):
        #cmd = cnc_direction + ' {:.2f/} F '.format(cnc_dist, self.cnc_feedrate)

        #self.logger.info('COMMAND: ' + str(cmd))

        try:
            state, pos = send_move_cmd(cnc_direction, cnc_dist)#self.cnc.send_move_command('G21 G91 ' + cmd)
            self.curr_camera_pos = pos
        except:
            self.logger.warn('Improper position command')

        self.logger.info(str(self.curr_camera_pos))

    def set_feedrate_cnc(self, cnc_feedrate):
        user_feedrate = input

        try:
            self.cnc.set_feedrate(cnc_feedrate)
            self.cnc_feedrate = cnc_feedrate
        except:
            self.logger.warn('Improper feedrate command')

    # def close_cnc(self):
    #     self.logger.info('Closing out...')
    #     self.cnc.close()
