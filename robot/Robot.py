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

# Subcomponents
from .actuators import CNC_Controller
#from .display/gui import *
from .passiveLighting import *
#from .activeLighting import *
from .piCamera import *
from .waterMechanism import *
from post_processing.stitching import stitch_images

sys.path.append(os.path.abspath('../post_processing'))


class Robot:

    sched = None

    h = httplib2.Http()

    curr_pos = [0,0]
    new_pos = [0,0]
    new_pos_abs = [0,0]
    water_amount = 0
    tube_fill = True


    COMMANDS = {
        "TAKE_IMAGE" : lambda self: self.takeCameraImage(),
        "PREVIEW_IMAGE" : lambda self: self.previewImage(),
        "ON_PL" : lambda self: self.passiveLightingOnOff(True),
        "OFF_PL" : lambda self: self.passiveLightingOnOff(),
        "ON_AL" : lambda self: self.activeLightingOnOff(True),
        "OFF_AL" : lambda self: self.activeLightingOnOff(),
        "ON_W" : lambda self: self.waterSystemOnOff(True),
        "OFF_W" : lambda self: self.waterSystemOnOff(),
        "WATER" : lambda self: self.waterSystemAmount(self.water_amount),
        "MOVE" : lambda self: self.perform_move(self.new_pos),
        "CNC_POS" : lambda self: self.set_pos_cnc(self.new_pos, False),
        "CNC_POS_ABS" : lambda self: self.set_pos_cnc(self.new_pos_abs, True),
        "GET_POS" : lambda self: self.get_pos_cnc(),
        "CAL" : lambda self: self.cnc_calibartion(),
        "ROUTE_Z" : lambda self: self.route_zigzag('route_zigzag', True),
        "ROUTE_L" : lambda self: self.route_line('route_line', True),
        "MAP" : lambda self: self.image_map_bed(),
        "X" : lambda self: self.close(),
        #watering
    }

    # --------------------------------------------------------------------------
    # ----------------------------- INITALIZATION ------------------------------
    # --------------------------------------------------------------------------

    def __init__(self, robot_id, logger, cnc_logger = None):
        self.robot_id = robot_id
        self.logger = logger

        #  ----- Initalize threading: Robot, API Interface ------
        self._q = Queue()
        self._stop_event = threading.Event()

        # Begin robot thread for handling motion and robot logs
        self.logger.info('Starting up robot thread')
        self.robot_thread = threading.Thread(target=self._robot_run)
        self.robot_thread.start()

        # Initializing API
        self.logger.info('Starting up API')
        self.api_interface = threading.Thread(target=self._api_interface)
        self.api_interface.start()

        # Initialize components
        self.logger.info('Initializing components...')

        self.passive_led = PassiveLEDs(RELAY_PIN_PL)
        self.logger.info(' - PASSIVE LIGHTING [READY]')

        self.watering_mechanism = WaterPump(RELAY_PIN_WATER)
        self.logger.info(' - WATERING MECHANISM [READY]')

        self.cnc = CNC_Controller(cnc_logger)
        self.logger.info(' - CNC CONTROLLER [READY]')

        self.camera = Camera()
        self.logger.info(' - CAMERA [READY]')

        # Initial actions
        self.logger.info('Initial robot actions...')
        #self.passive_led.turn_on()

        self.cnc.calibration()
        self.set_pos_cnc([0,50], True)

        #Send command to gardner that the robot is ready to start

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

        if command[0] == '[' or command[0] == '%':
            self.perform_move(command)
        elif command == 'WATER':
            self.water_amount = para
            self._q.put('WATER')
        else:
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


    # ---------------------------- WATERING SYSTEM -----------------------------

    # Turn watering system on or off
    def waterSystemOnOff(self, on = False):
        if on:
            self.watering_mechanism.turn_on()
            self.logger.info(' - Turning on watering system')
        else:
            self.watering_mechanism.turn_off()
            self.logger.info(' - Turning off watering system')

    def waterSystemAmount(self, water_amount):

        self.logger.info('Watering {} mL at [{}, {}]'.format(water_amount, self.curr_pos[0], self.curr_pos[1]))

        self.waterSystemOnOff(True)

        # Water for x time accounting for tube fill
        if self.tube_fill:
            time.sleep(int(water_amount) * WATER_COEF)
        else:
            time.sleep(int(water_amount) * WATER_COEF + 1)

        self.waterSystemOnOff(False)

        time.sleep(1)

        # Check tube filled
        if (self.curr_pos[0] > 0.50 * X_MAX):
            self.tube_fill = False
        else:
            self.tube_fill = True


    # ----------------------------------- CNC ----------------------------------

    # Move central mount a certain direction and distance
    def get_pos_cnc(self):
        self.logger.info('Current position: [{}, {}])'.format(self.curr_pos[0], self.curr_pos[1]))


    def set_pos(self, new_pos):
        abs_cmd = str(new_pos.split('[')[0]) is '%'

        pos = [0,0]

        pos[0] = int(new_pos.split('[')[1].split(',')[0])
        pos[1] = int(new_pos.split('[')[1].split(',')[1].split(']')[0])

        if abs_cmd:
            self.set_pos_cnc(pos, True)
        else:
            self.set_pos_cnc(pos, False)

    def set_pos_cnc(self, new_pos, abs = False):
        if abs:
            self.curr_pos = self.cnc.set_pos_abs(new_pos)
            self.logger.info('Current position: [{}%, {}%] - ([{}, {}])'.format(new_pos[0], new_pos[1], self.curr_pos[0], self.curr_pos[1]))

        else:
            self.curr_pos = self.cnc.set_pos(new_pos)
            self.logger.info('Current position: [{}, {}])'.format(self.curr_pos[0], self.curr_pos[1]))

    def perform_move(self, new_pos, abs = False):

        if '-' in new_pos:

            temp0 = new_pos.split(',')

            # Check diagonal line
            # still needs multi stepper movement
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

            self.set_pos(pos1)
            self.set_pos(pos2)

        else:
            self.logger.info('Moving to {}'.format(pos1))
            self.set_pos(new_pos)



    def cnc_calibartion(self):
        self.logger.info('Calibrating CNC...')
        self.cnc.calibration()
        #self.set_pos_cnc([0,50], True)
        self.logger.info('Calibration complete!')

    # ---------------------------------- ROUTE ---------------------------------

    def route_zigzag(self, tag = 'route_zigzag', return_origin = False):
        bound = 0
        pos_perc = [bound,bound]

        x_steps = 5
        y_steps = 1

        dir = 0

        self.logger.info('Starting zigzag route.... ({}, {})'.format(x_steps, y_steps))

        for j in range(0, y_steps+1):
            for i in range(0, x_steps+1):
                if j % 2 == 0:
                    pos_perc[1] = float(i)/y_steps*(100.0-2*bound) + bound
                else:
                    pos_perc[1] = (100 - bound) -float(i)/y_steps*(100.0-2*bound)

                pos_perc[0] = float(j)/x_steps*(100.0-2*bound) + bound

                self.curr_pos = self.set_pos_cnc(pos_perc, True)

                self.route_action('{}_{}_{}.png'.format(tag, i,j))

        self.logger.info('Zigzag route Complete ({}, {})!'.format(x_steps, y_steps))

        if return_origin:
            self.cnc.calibration()
            self.logger.info('Returning to origin')

    def route_line(self, tag = 'route_line', return_origin = False):
        bound = 0
        pos_perc = [bound,50]

        x_steps = 5

        dir = 0

        self.logger.info('Starting line route.... ({})'.format(x_steps))

        for j in range(0, x_steps+1):

            pos_perc[0] = float(j)/x_steps*(100.0-2*bound) + bound

            self.curr_pos = self.set_pos_cnc(pos_perc, True)

            self.route_action('{}_{}.png'.format(tag,j))

        self.logger.info('Line route Complete ({})!'.format(x_steps))

        if return_origin:
            #self.cnc.calibration()
            self.set_pos_cnc([0,50], True)
            self.logger.info('Returning to origin')

    def route_action(self, tag):
        image_file = '/home/pi/plantMonitor/data/raw_images/{}'.format(tag)
        self.logger.info('Saving image to ' + str(image_file))
        self.takeCameraImage(image_file)

    def image_map_bed(self):
        tag = 'imagemap'

        image_dir = '/home/pi/plantMonitor/data/raw_images/'

        try:
            os.remove('{}/{}*'.format(image_dir, tag))
        except OSError:
            pass

        # Get images
        self.logger.info('Mapping bed...')
        self.route_line(tag, True)
        self.logger.info('Mapping finished!')

        # Stitch images into panorama

        output_file = '/home/pi/plantMonitor/data/result_images/bed_scan_map_{}.png'.format(time.strftime("%Y-%m-%d_%H_%M_%S",time.gmtime()))

        self.logger.info('Stitching together images to form panorama...')
        try:
            stitch_images(image_dir, output_file, '{}*.png'.format(tag))
        except Exception as e:
            self.logger.warn('Stitching failed!')
        else:
            self.logger.info('Panorama created!!')
