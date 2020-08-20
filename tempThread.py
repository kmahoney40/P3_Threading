import threading
import time
from ad_board import ADBoard 


# The daqcThread calss will read/write the daqc-plate and a relay-plate to monitor temps in and
# outside of the garage and control an exhaust fan.
class daqcThread(threading.Thread):
    def __init__(self, threadID, name, in_dict, event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict
        self.event = event
        self.adc = ADBoard(0, event)

    def run(self):
        #print("Starting " + self.name)
        while not self.event.is_set():            
            self.in_dict[0] += 1
            #time.sleep(5)
            for t in range(3):
                self.in_dict[t] = self.adc.get_adc(t)
            self.event.wait(timeout=5)

