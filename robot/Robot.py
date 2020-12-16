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

from os import path
from queue import *
from subprocess import check_output, Popen, PIPE

from .robot_config import *

#Subcomponents
#from .actuators import *
#from .display import *
from .passiveLighting import *
#from .activeLighting import *
from .piCamera import *
#from .sensors import Lock_Sensor, Relay_Sensor, Battery_Sensor

class Robot:

    sched = None

    COMMANDS = {
        "On" : lambda self: self.passiveLightingOnOff(True),
        "Off" : lambda self: self.passiveLightingOnOff(),
        #"TurnOnActiveLights" : lambda self: self.activeLightingOnOff(True),
        #"TurnOffActiveLights" : lambda self: self.activeLightingOnOff(),
        "TakeImage" : lambda self: self.takeCameraImage(),
        "T" : lambda self: self.temp(),
        "X" : lambda self: self.close(),
        #motion
        #watering
    }

    # -------------- INITALIZATION ----------------------

    def __init__(self, robot_id, logger):
        self.robot_id = robot_id
        self.logger = logger

        #self.uart = uart
        #self.servo = Servo()
        #self.oled = Oled()

        #  ----- Initalize threading: Robot, API Interface ------
        self._q = Queue()
        self._stop_event = threading.Event()

        # Begin robot thread for handling motion and robot logs
        self.robot_thread = threading.Thread(target=self._robot_run)
        self.robot_thread.start()

        self.passive_led = PassiveLEDs()
        self.camera = Camera()
        #if API_YES_NO:
        #    self.api_interface = threading.Thread(target=self._api_interface)
        #    self.api_interface.start()

        self.logger.info('Robot setup complete!')

    # Stop threads and close out of all objects
    def close(self):

        self.passive_led.close()

        self._stop_event.set()

        #self.robot_thread.join() # Stop robot thread
        #self.api_interface.join() # Stop oled thread

        #self.oled.close()
        #self.servo.close()

    # Define scheduler
    def register_scheduler(self, sched):
        self.sched = sched

    # Get the robot_id
    def get_robot_id(self):
        return self.robot_id

    # -------------- THREADED FUNCTIONS ----------------------

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
            # Monitor action list
            action_cmd = 'curl -X GET http://localhost:5002/action/'
            action_result = check_output(action_cmd, stdin=PIPE, stderr=PIPE, shell = True)
            action_r = action_result.decode("utf-8")
            action_json = json.loads(action_r)

            # Process action either immediately or add to schedule
            if action_json['Action'] != '':
                print(action_json)
                if action_json['Date'] == '':
                    self.queue_command_plus(action_json['Action'])
                else:
                    self.add_command_to_schedule(action_json['Date'], action_json['Action'])

            # Pause before pinging api
            time.sleep(1)


    # -------------- COMMAND & QUEUE FUNCTIONS ----------------------

    # Run the commmand immediately
    def command(self, command):
        for key, value in self.COMMANDS.items():
            if key == command:
                value(self)
                break

    # Queue a command under the threaded function
    def queue_command(self, command):
        self._q.put(command)

    # Adds api input to schedule csv
    def add_command_to_schedule(self, date, command):

        #new_scheduled_time = date.strftime(SCHED_FMT)
        with open(SCHED_CSV, 'w+') as schedule_file:
            scheduler = csv.writer(schedule_file)#, delimiter=',')
            scheduler.writerow([date, command])

    # -------------- MAIN ACTIONS ----------------------

    def passiveLightingOnOff(self, on = False):
        if on:
            self.passive_led.turn_on()
            self.logger.info('Turning on Passive Lighting')
        else:
            self.passive_led.turn_off()
            self.logger.info('Turning off Passive Lighting')

    def activeLightingOnOff(self, on = False):
        self.logger.info('Active Lighting On / Off')

    def activeLightingColor(self):
        self.logger.info('Active Lighting Color')

    def takeCameraImage(self):
        self.camera.capture('foo.jpg')
        self.logger.info('Image captured from picamera')
