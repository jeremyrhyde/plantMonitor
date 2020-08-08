#!/usr/bin/env python3
"""UART Test
Create a virtual UART and simulate log messages

Usage:
  uart_test.py <log-file> [--time]
  uart_test.py -h | --help
  uart_test.py -v | --version

Options:
  -t  --time     Simulate timing
  -h  --help     Show this screen.
  -v  --version  Show version.

"""

import os
import pty
import re
import threading
from docopt import docopt
from collections import namedtuple
from queue import PriorityQueue
from datetime import datetime, timedelta


class Virtual_UART_Interface:

    MSG_DELAY = 0.2

    _Message = namedtuple("UART_Message", "time msg")

    _q = PriorityQueue()
    _log_time = re.compile(r"^\[([^\]]+)")
    _log_msg = re.compile(r"^\[[^\]]+\] (.*)")
    _time_format = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, baudrate, simulate_time=True):
        self.simulate_time = simulate_time

        self._master, self._slave = pty.openpty()
        self.serial_name = os.ttyname(self._slave)

        self._thread = threading.Thread(target=self._simulate)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread.start()

    # Write to serial
    def write(self, msg):
        with self._lock:
            os.write(self._master, msg.encode("utf-8"))

    def is_real(self):
        return False

    # Close the serial port
    def close(self):
        self._stop_event.set()
        self._thread.join()

    def join(self):
        return self._q.join()

    # Queues the next uart message to be written
    # Assumes the uart message has a timestamp with format
    # Format is based on teraterm
    def queue_message(self, msg):
        time_str = self._log_time.search(msg).group(1)
        uart_msg = self._log_msg.search(msg).group(1)
        time_msg = datetime.strptime(time_str, self._time_format)

        q_msg = self._Message(time_msg, uart_msg)
        self._q.put(q_msg)

    def load_file(self, file_path):
        with open(file_path) as fp:
            for _, line in enumerate(fp):
                if line.strip():
                    self.queue_message(line.strip())

    def _simulate(self):
        prev_time = None
        message = None

        while not self._stop_event.is_set():
            if message is None and not self._q.empty():
                message = self._q.get(block=True)

                if prev_time is None:
                    prev_time = message.time

                if self.simulate_time:
                    next_transmit = datetime.now() + (message.time - prev_time)
                else:
                    next_transmit = datetime.now() + timedelta(seconds=self.MSG_DELAY)

            if message and datetime.now() >= next_transmit:
                self.write(message.msg + "\r\n")
                self._q.task_done()
                prev_time = message.time
                message = None


def main(args):
    log_file = args["<log-file>"]
    simulate_time = args["--time"]

    test_uart = Virtual_UART_Interface(115200, simulate_time)
    print(test_uart.serial_name)

    test_uart.load_file(log_file)

    test_uart.join()
    test_uart.close()


if __name__ == "__main__":
    args = docopt(__doc__, version="0")
    main(args)
