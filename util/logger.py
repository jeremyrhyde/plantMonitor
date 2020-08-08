#!/usr/bin/env python3
"""Logger file
This file contains a logging helper class
"""

import sys
import logging
from enum import Flag, auto
from datetime import datetime

class Logger:

    _parser = None

    # Binary configuration for logging
    class Log_Config(Flag):
        PARSE_STREAM_LOG = auto()
        STREAM_LOG = auto()
        PARSE_FILE_LOG = auto()
        FILE_LOG = auto()

    def __init__(self, parser=None):
        self._parser = parser

        self._log_methods = {
            self.Log_Config.PARSE_STREAM_LOG: lambda self: self._get_stream_handler(True),
            self.Log_Config.STREAM_LOG: lambda self: self._get_stream_handler(),
            self.Log_Config.PARSE_FILE_LOG: lambda self: self._get_file_handler(True),
            self.Log_Config.FILE_LOG: lambda self: self._get_file_handler(),
        }

    def close(self):
        if self._parser:
            self._parser.close()

    def _get_stream_handler(self, parse=False):
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        if parse:
            if self._parser:
                formatter = logging.Formatter(
                    "%(asctime)s [PARSER] %(levelname)s - %(parse)s"
                )
                handler.addFilter(self._parser)
            else:
                raise RuntimeError("Parser not set!").with_traceback(sys.exc_info()[2])
        else:
            formatter = logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s - %(message)s"
            )

        handler.setFormatter(formatter)

        return handler

    # ToDo
    def _get_file_handler(self, parse=False):
        #filename = "logs/UART_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
        filename = "logs/UART.log"

        handler = logging.FileHandler(filename)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s [FILE] %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # if parse:
        #    if self._parser:
        #        handler.addFilter(self._parser)
        #    else:
        #        raise RuntimeError('Parser not set!').with_traceback(sys.exc_info()[2])

        return handler

    # Initialize the logger and return it
    def init(self, log_type, log_id, log_method=Log_Config.STREAM_LOG):

        # Set the logger name
        logger = logging.getLogger(log_type + " " + log_id)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        # Configure the logger
        for config in self.Log_Config:
            # Bitwise AND to get logging method
            method = log_method & config

            handler = self._log_methods.get(method, None)
            if handler is not None:
                logger.addHandler(handler(self))

        logger.info("Logging initialized...")
        return logger
