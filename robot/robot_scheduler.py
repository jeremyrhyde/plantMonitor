#!/usr/bin/env python3
"""Schedule robot actions from CSV file
"""

import os, sys

sys.path.insert(0, os.getcwd())

import csv
import pytz
import time
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

from .robot_config import DAILY_CSV, SCHED_CSV, DAILY_FMT, SCHED_FMT, OLED_FMT, TIMEZONE
from .Robot import Robot
#from .robot_M2 import Robot_M2
from util import Logger

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]


class Robot_Scheduler:

    DAILY_PATH = os.path.normpath(DAILY_CSV)
    SCHED_PATH = os.path.normpath(SCHED_CSV)

    daily_tasks = []
    sched_tasks = []
    sorted_jobs = []

    # This is a handler to register with the filesystem observer
    class FileHandler(FileSystemEventHandler):
        def __init__(self, action):
            self._action = action

        def on_any_event(self, event):
            self._action(event)

    def __init__(self, robot):
        self.robot = robot

        self.sched = BackgroundScheduler()
        self.sched.start()

        # This will take a long time to execute
        self.init_actions(self.DAILY_PATH, True)
        self.init_actions(self.SCHED_PATH, False)

        self.event_handler = self.FileHandler(self.csv_handler)
        self.obs = Observer()
        self.obs.schedule(self.event_handler, path="./logs/", recursive=True)
        self.obs.start()

    # Clean up
    def close(self):
        self.obs.stop()
        self.obs.join()

    def clear(self, job_list):
        for i in list(job_list):
            try:
                i.remove()
            except JobLookupError:
                pass
        job_list.clear()

    # This function is called every time the file system changes
    def csv_handler(self, event):
        e_path = os.path.normpath(event.src_path)

        if e_path == self.DAILY_PATH:
            self.clear(self.daily_tasks)
            self.init_actions(DAILY_CSV, True)
        elif e_path == self.SCHED_PATH:
            self.clear(self.sched_tasks)
            self.init_actions(SCHED_CSV, False)

    # Parse the time into a time object
    def parse_time(self, time_str, daily):
        if daily:
            return datetime.strptime(time_str, DAILY_FMT)
        else:
            return datetime.strptime(time_str, SCHED_FMT)

    def get_next_job(self):
        jobs = self.sched.get_jobs()

        if jobs:
            sorted_jobs = sorted(jobs, key=lambda job: job.next_run_time)

            time_job = sorted_jobs[0].next_run_time
            time_now = datetime.now(pytz.timezone(TIMEZONE))

            time_str = time_job.strftime(OLED_FMT)

            time_remaining = int((time_job - time_now).total_seconds())
            time_str += str(time_remaining)

            return sorted_jobs[0].name, time_str

        time_now = datetime.now(pytz.timezone(TIMEZONE))
        time_str = time_now.strftime(OLED_FMT)
        return "IDLE", time_str

    # Schedules both daily and scheduled actions into the scheduler
    def sched_actions(self, t, command, daily):

        cmd_name = command

        if daily:
            # Cron style daily scheduling
            task = self.sched.add_job(
                self.robot.queue_command,
                name=cmd_name,
                trigger="cron",
                args=[command.strip()],
                hour=t.hour,
                minute=t.minute,
                second=t.second,
                timezone=pytz.timezone(TIMEZONE),
            )
            self.daily_tasks.append(task)
        else:
            # Date based scheduling
            task = self.sched.add_job(
                self.robot.queue_command,
                name=cmd_name,
                trigger="date",
                args=[command.strip()],
                run_date=t,
                timezone=pytz.timezone(TIMEZONE),
            )
            self.sched_tasks.append(task)

    def mycsv(self, csv_reader):
        while True:
            try:
                yield next(csv_reader)
            except csv.Error:
                pass
            except StopIteration:
                return
            continue
        return

    # Initializes actions from the csv file
    def init_actions(self, csv_file, daily):
        with open(csv_file, mode="r", encoding="utf-8-sig") as f:
            reader = self.mycsv(csv.DictReader(f, fieldnames=["time", "action"]))

            for row in reader:
                t = self.parse_time(row["time"], daily)
                self.sched_actions(t, row["action"], daily)


def main():
    logger = Logger()

    robot_id = "000"
    robot_logger = logger.init("ROBOT", robot_id)
    my_robot = Robot(robot_id, robot_logger, True, test_mode=True)

    mon = Robot_Scheduler(my_robot)

    print("TESTING")
    mon.get_next_job()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mon.close()

    print("Exiting...")


if __name__ == "__main__":
    main()
