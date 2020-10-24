import threading
import time
from ad_board import ADBoard 


# The daqcThread class will read/write the daqc-plate and a relay-plate to monitor temps in and
# outside of the garage and control an exhaust fan.
class daqcThread(threading.Thread):
    def __init__(self, threadID, name, logger, in_dict, event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict
        self.ll = logger
        self.event = event
        self.adc = ADBoard(0, logger, event)

    def run(cls):
        while not cls.event.is_set():
            cls.ll.log("DEBUG d", "d")
            cls.ll.log("INFO i", "i")
            cls.ll.log("WARNING w", "w")
            cls.ll.log("ERROR e", "e")
            cls.ll.log("CRITICAL c", "c")

            for t in range(3):
                cls.in_dict[t] = cls.adc.get_adc_filter(t)
            cls.ll.log("Temp Thread")
            cls.event.wait(timeout=5.0)
