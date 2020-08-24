import threading
import time
from relay_board import RelayBoard


# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class sprinklerThread(threading.Thread):
    def __init__(self, threadID, name, in_dict, event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict
        self.wait_time = 1#cfgObj.wait_time
        self.event = event
        self.relay_board = RelayBoard(0, event)

    def run(cls):
        while not cls.event.is_set():
            cls.in_dict[0] += 1
            idx = cls.in_dict[0]
            #cls.relay_board.relay_toggle(2)
            cls.relay_board.toggle_led(0)
            cls.event.wait(timeout=1)
