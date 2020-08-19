import threading
import time



# The daqcThread calss will read/write the daqc-plate and a relay-plate to monitor temps in and
# outside of the garage and control an exhaust fan.
class daqcThread(threading.Thread):
    def __init__(self, threadID, name, in_dict, event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict
        self.event = event

    def run(self):
        #print("Starting " + self.name)
        while not self.event.is_set():            
            self.in_dict[0] += 1
            #time.sleep(5)
            self.event.wait(timeout=5)

