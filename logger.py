import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

class logger:
    def __init__(self, file_name, log_level):
        self.today = datetime.date.today()
        self.file_name = file_name
        #log_file = self.file_name + "_" + str(self.today) + ".log"

        self.l_level = ""
        if log_level == "DEBUG":
            self.l_level = logging.DEBUG
        if log_level == "INFO":
            self.l_level = logging.INFO
        if log_level == "WARNING":
            self.l_level = logging.WARNING
        if log_level == "ERROR":
            self.l_level = logging.ERROR
        if log_level == "CRITICAL":
            self.l_level = logging.CRITICAL


        log_file = '/var/log/automation/' + self.file_name + "_" + str(self.today) + '.log'
        logging.basicConfig(filename=log_file, level=self.l_level)
        self.logger = logging.getLogger("Rotating Log")
        self.logger.setLevel(self.l_level)
        #self.logger.setLevel(logging.INFO)
        log_file = "/var/log/automation/water.log"
        self.handler = TimedRotatingFileHandler(log_file,
                                            when="midnight",
                                            interval=1,
                                            backupCount=5)
        self.logger.addHandler(self.handler)
        
    #def __init__

    def update_log_level(cls, log_level):
        local_level = 0
        if log_level == "DEBUG":
            local_level = logging.DEBUG
        if log_level == "INFO":
            local_level = logging.INFO
        if log_level == "WARNING":
            local_level = logging.WARNING
        if log_level == "ERROR":
            local_level = logging.ERROR
        if log_level == "CRITICAL":
            local_level = logging.CRITICAL
        cls.logger.setLevel(local_level)

    def log(cls, msg, lvl="i"):
        new_day = datetime.date.today()
        dtnow = str(datetime.datetime.now()) + " "

        if lvl.lower() == "d":
            cls.logger.debug(dtnow + "DEBUG: " + msg)
        if lvl.lower() == "i":
            cls.logger.info(dtnow + "INFO: " + msg)
        if lvl.lower() == "w":
            cls.logger.warning(dtnow + "WARNING: " + msg)
        if lvl.lower() == "e":
            cls.logger.error(dtnow + "ERROR: " + msg)
        if lvl.lower() == "c":
            cls.logger.critical(dtnow + "CRITICAL: " + msg)

    # def log()
# class Logger
