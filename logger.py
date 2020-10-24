import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

class logger:
    def __init__(self, file_name, log_level):
        self.today = datetime.date.today()
        self.file_name = file_name
        #log_file = self.file_name + "_" + str(self.today) + ".log"

        l_level = "bob"
        if log_level == "DEBUG":
            l_level = logging.DEBUG
        if log_level == "INFO":
            l_level = logging.INFO
        if log_level == "WARNING":
            l_level = logging.WARN
        if log_level == "ERROR":
            l_level = logging.ERROR
        if log_level == "CRITICAL":
            l_level = logging.CRITICAL


        log_file = '/var/log/automation/' + self.file_name + "_" + str(self.today) + '.log'
        logging.basicConfig(filename=log_file, level=l_level)
        self.logger = logging.getLogger("Rotating Log")
        #self.logger.setLevel(logging.INFO)
        log_file = "/var/log/automation/water.log"
        self.handler = TimedRotatingFileHandler(log_file,
                                            when="midnight",
                                            interval=1,
                                            backupCount=5)
        self.logger.addHandler(self.handler)
        
        
        
    #def __init__

    def log(cls, msg, lvl="i"):
        new_day = datetime.date.today()
        dtnow = str(datetime.datetime.now()) + " "

        #if new_day != cls.today:
            # cls.today = new_day
            # log_file = cls.file_name + "_" + str(cls.today) + ".log"
            # logging.basicConfig(filename=log_file)


        if lvl.lower() == "d":
            cls.logger.debug(dtnow + msg)
        if lvl.lower() == "i":
            cls.logger.info(dtnow + msg)
        if lvl.lower() == "w":
            cls.logger.warning(dtnow + msg)
        if lvl.lower() == "e":
            cls.logger.error(dtnow + msg)
        if lvl.lower() == "c":
            cls.logger.critical(dtnow + msg)

    # def log()
# class Logger
