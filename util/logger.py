import logging
import os

class Logger:
    def __init__(self, log_type, log_id):
        self.log_type = log_type
        self.log_id = log_id

        # self._log_methods = {
        #     #self.Log_Config.PARSE_STREAM_LOG: lambda self: self._get_stream_handler(True),
        #     self.Log_Config.STREAM_LOG: lambda self: self._get_stream_handler(),
        #     self.Log_Config.FILE_LOG: lambda self: self._get_file_handler(),
        # }

    def init(self, log_name, log_file, level=logging.INFO):

        FORMAT = '%(asctime)s [' + self.log_type + '] [' + self.log_id + '] %(levelname)s - %(message)s'
        formatter = logging.Formatter(FORMAT)

        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        logger.addHandler(handler)

        #logger.propagate = False

        return logger

    def clear_log_file(self, log_file):

        if os.path.isfile(log_file):
            os.system('rm ' + log_file)
        os.system('touch ' + log_file)

if __name__ == '__main__':
    # first file logger
    log_file = 'first_logfile.log'
    logger = Logger('PHONE', '0003030')

    logger.clear_log_file(log_file)
    logger_DUT = logger.init('first_logger', 'first_logfile.log')
    logger_DUT.info('This is just info messa2ge')

    # second file logger
    logger_DUT_super = logger.init('second_logger', 'second_logfile.log')
    logger_DUT_super.error('This is an error messag2e')
