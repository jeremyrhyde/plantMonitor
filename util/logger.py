import logging
import os

class Logger:

    def __init__(self, log_file, clear_log = False):
        self.log_file = log_file

        if clear_log: self.clear_log_file()

    def init(self, log_name, log_id, level=logging.INFO):

        FORMAT = '%(asctime)s [' + log_name + '] [' + log_id + '] %(levelname)s | %(message)s'
        formatter = logging.Formatter(FORMAT)

        handler_file = logging.FileHandler(self.log_file)
        handler_file.setFormatter(formatter)

        handler_stream = logging.StreamHandler()
        handler_stream.setFormatter(formatter)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)

        #logger.propagate = False

        return logger

    def clear_log_file(self):

        if os.path.isfile(self.log_file):
            os.system('rm ' + self.log_file)
        os.system('touch ' + self.log_file)

    def close(self):
        pass

if __name__ == '__main__':

    logger = Logger('temp.log')
    log = logger.init('ROBOT', '000')
    log.info('logger message')
