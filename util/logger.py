import logging
import os

class Logger:

    def __init__(self, log_file):
        self.log_file = log_file

        self.clear_log_file()
        #self.log_type = log_type
        #self.log_id = log_id

        # self._log_methods = {
        #     #self.Log_Config.PARSE_STREAM_LOG: lambda self: self._get_stream_handler(True),
        #     self.Log_Config.STREAM_LOG: lambda self: self._get_stream_handler(),
        #     self.Log_Config.FILE_LOG: lambda self: self._get_file_handler(),
        # }

    def init(self, log_name, level=logging.INFO):

        FORMAT = '%(asctime)s [' + log_name + '] %(levelname)s - %(message)s'
        formatter = logging.Formatter(FORMAT)

        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(formatter)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        logger.addHandler(handler)

        #logger.propagate = False

        return logger

    def clear_log_file(self):

        if os.path.isfile(self.log_file):
            os.system('rm ' + self.log_file)
        os.system('touch ' + self.log_file)

if __name__ == '__main__':

    logger = Logger('temp.log')
    log = logger.init('ROBOT')
    log.info('logger message')
