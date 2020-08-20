import logging
import datetime

class logger:
    def __init__(self, file_name):
        self.today = datetime.date.today()
        self.file_name = file_name
        log_file = self.file_name + "_" + str(self.today) + ".log"
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
    #def __init__

    def log(cls, msg, lvl="i"):
        new_day = datetime.date.today()
        dtnow = str(datetime.datetime.now()) + " "
        if new_day != cls.today:
            cls.today = new_day
            log_file = cls.file_name + "_" + str(cls.today) + ".log"
            loggind.basicConfig(filename=log_file)
        if lvl.lower() == "i":
            logging.info(dtnow + msg)
        if lvl.lower() == "d":
            logging.info(dtnow + msg)
        if lvl.lower() == "w":
            logging.info(dtnow + msg)

    # def log()
# class Logger
