import threading
import time


# This calss will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictioary can be expanded to include weahter data that may be used
# to dynamically modife runtimes.
class sprinklerThread(threading.Thread):
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
            #time.sleep(1)
            self.event.wait(timeout=1)

