#!/usr/bin/env python3

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

from .overseer_config import *
from .plant_dict import *

class Overseer:

    h = httplib2.Http()

    plant_name = ''


    COMMANDS = {
        "WATER" : lambda self: self.water(),
    }


    def __init__(self, logger):
        self.logger = logger

        self.plant_list = plant_dict

        self._q = Queue()
        self._stop_event = threading.Event()

        # Begin robot thread for handling motion and robot logs
        self.logger.info('Starting up overseer thread')
        self.overseer_thread = threading.Thread(target=self._overseer_run)
        self.overseer_thread.start()

        self.register_schedule()


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
            self.plant_name = para

        self._q.put(command)

    def register_schedule(self):
        pass

    def water(self):
        pass
