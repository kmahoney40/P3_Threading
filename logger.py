import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

class logger:
    def __init__(self, file_name):
        self.today = datetime.date.today()
        self.file_name = file_name
        #log_file = self.file_name + "_" + str(self.today) + ".log"
        log_file = '/var/log/automation/' + self.file_name + "_" + str(self.today) + '.log'
        #logging.basicConfig(filename=log_file, level=logging.DEBUG)
        self.logger = logging.getLogger("Rotating Log")
        self.logger.setLevel(logging.INFO)
        log_file = "/var/log/automation/water.log"
        self.handler = TimedRotatingFileHandler(log_file,
                                            when="h",
                                            #interval=1,
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


        if lvl.lower() == "i":
            #logging.info(dtnow + msg)
            cls.logger.info(dtnow + msg)
        if lvl.lower() == "w":
            #logging.warning(dtnow + msg)
            cls.logger.warning(dtnow + msg)
        if lvl.lower() == "e":
            #logging.error(dtnow + msg)
            cls.logger.error(dtnow + msg)
        if lvl.lower() == "d":
            #logging.debug(dtnow + msg)
            cls.logger.debug(dtnow + msg)

    # def log()
# class Logger
