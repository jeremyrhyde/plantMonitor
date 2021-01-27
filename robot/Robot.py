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
from .waterMechanism import *
#from .sensors import Lock_Sensor, Relay_Sensor, Battery_Sensor

class Robot:

    sched = None

    h = httplib2.Http()

    cnc_direction = ''
    cnc_dist = ''
    cnc_feedrate = ''
    new_pos = ''

    COMMANDS = {
        "TAKE_IMAGE" : lambda self: self.takeCameraImage(),
        "PREVIEW_IMAGE" : lambda self: self.previewImage(),
        "ON_PL" : lambda self: self.passiveLightingOnOff(True),
        "OFF_PL" : lambda self: self.passiveLightingOnOff(),
        #"ON_AL" : lambda self: self.activeLightingOnOff(True),
        #"OFF_AL" : lambda self: self.activeLightingOnOff(),
        "ON_W" : lambda self: self.waterSystemOnOff(True),
        "OFF_W" : lambda self: self.waterSystemOnOff(),
        "CNC_MOTION" : lambda self: self.move_cnc(self.cnc_direction, self.cnc_dist),
        "CNC_POS" : lambda self: self.set_pos_cnc(self.new_pos),
        "CNC_FEEDRATE" : lambda self: self.set_feedrate_cnc(self.cnc_feedrate),
        "ROUTE_Z" : lambda self: self.route_zigzag(True),
        "ROUTE_L" : lambda self: self.route_line('route_line', True),
        "MAP" : lambda self: self.image_map_bed(),
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
        self.passive_led = PassiveLEDs(RELAY_PIN_PL)
        self.watering_mechanism = WaterPump(RELAY_PIN_WATER)

        self.cnc = GRBL_Stream(RELAY_PIN_CNC, X_MAX, Y_MAX)
        self.cnc_feedrate = self.cnc.get_feedrate()
        self.curr_pos = self.cnc.get_pos()

        self.camera = Camera()

        # Begin API
        self.api_interface = threading.Thread(target=self._api_interface)
        self.api_interface.start()

        self.logger.info('Robot setup complete!')

    # Stop threads and close out of all objects
    def close(self):

        self.cnc.close()
        self.passive_led.close()
        self.cnc.close()
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

        if command == 'CNC_POS':
            self.new_pos = para[1:-1].split(',')

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
    def takeCameraImage(self, image_file='foo.png'):
        self.camera.image_capture(image_file)
        self.logger.info('Image captured from picamera')

    # View preview for 5 seconds
    def previewImage(self):
        self.camera.preview_5s()
        self.logger.info('Previewing image from picamera')


    # ---------------------------- PASSIVE LIGHTING ----------------------------

    def passiveLightingOnOff(self, on = False):
        if on:
            self.passive_led.turn_on()
            self.logger.info('Turning on passive lighting')
        else:
            self.passive_led.turn_off()
            self.logger.info('Turning off passive lighting')


    # ----------------------------- ACTIVE LIGHTING ----------------------------

    # def activeLightingOnOff(self, on = False):
    #     self.logger.info('Active Lighting On / Off')
    #
    # def activeLightingColor(self):
    #     self.logger.info('Active Lighting Color')


    # ---------------------------- PASSIVE LIGHTING ----------------------------

    # Turn watering system on or off
    def waterSystemOnOff(self, on = False):
        if on:
            self.watering_mechanism.turn_on()
            self.logger.info('Turning on watering system')
        else:
            self.watering_mechanism.turn_off()
            self.logger.info('Turning off watering system')


    # ----------------------------------- CNC ----------------------------------

    # Move central mount a certain direction and distance
    def move_cnc(self, cnc_direction, cnc_dist):
        try:
            state, pos = self.cnc.send_move_cmd(cnc_direction, cnc_dist)#self.cnc.send_move_command('G21 G91 ' + cmd)
        except:
            self.logger.warn('Improper position command')

        self.curr_pos = self.cnc.get_pos()
        self.logger.info('Current position: ' + str(self.curr_pos))

    # Move central mount a certain direction and distance
    def set_pos_cnc(self, new_pos, abs = True):
        try:
            if abs:
                state, pos = self.cnc.set_pos_absolute(new_pos)#self.cnc.send_move_command('G21 G91 ' + cmd)
            else:
                state, pos = self.cnc.set_pos(new_pos)
        except:
            self.logger.warn('Improper position command')

        self.curr_pos = self.cnc.get_pos()
        self.logger.info('Current position: ' + str(self.curr_pos))



    # Set feedrate for cnc
    def set_feedrate_cnc(self, cnc_feedrate):
        try:
            self.cnc.set_feedrate(cnc_feedrate)
            self.cnc_feedrate = cnc_feedrate
        except:
            self.logger.warn('Improper feedrate command')


    # ---------------------------------- ROUTE ---------------------------------

    def route_zigzag(self, return_origin = False):
        bound = 2.5
        pos_perc = [bound,bound]

        x_steps = 1
        y_steps = 5

        dir = 0

        self.logger.info('Starting zigzag route.... ({}, {})'.format(x_steps, y_steps))

        for j in range(0, y_steps+1):
            for i in range(0, x_steps+1):
                if j % 2 == 0:
                    pos_perc[0] = float(i)/x_steps*(100.0-2*bound) + bound
                else:
                    pos_perc[0] = (100 - bound) -float(i)/x_steps*(100.0-2*bound)

                pos_perc[1] = float(j)/y_steps*(100.0-2*bound) + bound

                self.set_pos_cnc(pos_perc)

                self.route_action('route_zigzag_{}_{}.png'.format(i,j))

                self.curr_pos = self.cnc.get_pos()
                self.logger.info('Current position: ' + str(self.curr_pos))

        self.logger.info('Zigzag route Complete ({}, {})!'.format(x_steps, y_steps))

        if return_origin:
            self.set_pos_cnc([bound,bound])
            self.logger.info('Returning to origin')

    def route_line(self, tag = 'route_line', return_origin = False):
        bound = 2.5
        pos_perc = [50,bound]

        y_steps = 5

        dir = 0

        self.logger.info('Starting line route.... ({})'.format(y_steps))

        for j in range(0, y_steps+1):


            pos_perc[1] = float(j)/y_steps*(100.0-2*bound) + bound

            self.set_pos_cnc(pos_perc)

            self.route_action('{}_{}.png'.format(tag,j))

            self.curr_pos = self.cnc.get_pos()
            self.logger.info('Current position: ' + str(self.curr_pos))

        self.logger.info('Line route Complete ({})!'.format(y_steps))

        if return_origin:
            self.set_pos_cnc([bound,bound])
            self.logger.info('Returning to origin')

    def route_action(self, tag):
        image_file = '/home/pi/plantmonitor/data/raw_images/{}'.format(tag)
        self.takeCameraImage(image_file)

    def image_map_bed(self):
        # Get images
        self.route_line('imagemap', True)

        # Stitch images into panorama
        input_dir = '/home/pi/plantMonitor/data/raw_images/'
        output_dir = '/home/pi/plantMonitor/data/result_images/'
        stitch_images(input_dir, output_dir)


    def route_action(self, tag):
        image_file = '/home/pi/plantmonitor/data/raw_images/{}'.format(tag)
        self.takeCameraImage(image_file)
