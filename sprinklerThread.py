import threading
import time
from datetime import datetime
from relay_board import RelayBoard
import logger
import json



# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class sprinklerThread(threading.Thread):
    def __init__(self, threadID, name, in_dict, event, update_event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger.logger("sprinklerThread __int__ called")
        self.in_dict = in_dict
        self.wait_time = 1#cfgObj.wait_time
        self.event = event
        self.update_event = update_event
        self.relay_board = RelayBoard(0, event)
        self.rt = [0, 2, 0, 2, 0, 5, 2, 0]
        self.rtt = [0, 2, 2, 4, 4, 9, 11, 11]
        self.rts = [0, 120, 120, 360, 360, 660, 780, 780]
        #self.rts = list(map(lambda x:self.start_time+x, self.rts))
        # The days of the week Mon = 0, Tue = 1...
        self.day = datetime.today().weekday()
        
        # Read conf file
        confFile = open("irrigation.conf", "r")
        confData = confFile.read()
        confJson = json.loads(confData)
        self.run_times = confJson["runTimes"]
        self.ll.log("confJson.[startTime]: " + str(confJson["startTime"]))
        self.ll.log("run_times: " + str(self.run_times[0]))
        
        self.start_time = confJson["startTime"]# * 60 * 60
        hours = self.start_time // 100
        min = self.start_time - (hours * 100)
        self.start_time = 60 * (hours * 60 + min)
        self.ll.log("confJson.[startTime]: " + str(self.start_time))
        
        for d in range(7):
            for v in range(1,8):
                self.run_times[d][v] += self.run_times[d][v-1]

            self.ll.log("BEFORE run_times[d]: " + str(self.run_times[d]))
            self.run_times[d] = list(map(lambda x:((x*60)+self.start_time), self.run_times[d]))
            self.ll.log("AFTER  run_times[d]: " + str(self.run_times[d]))
        
        
    # __init__
    
    def run(cls):
        while not cls.event.is_set():
            cls.in_dict[0] += 1
            idx = cls.in_dict[0]
            
            from_mid = datetime.now()
            now = datetime.now()
            now_in_sec = (now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds()
            cls.ll.log("now_in_sec: " + str(now_in_sec))
            cls.day = datetime.today().weekday()
            cls.ll.log("day: " + str(cls.day))
            cls.ll.log("cls.run_times[cls.day][0] " + str(cls.run_times[cls.day][0]))
            cls.ll.log("cls.run_times[cls.day][7] " + str(cls.run_times[cls.day][7]))

            if cls.run_times[cls.day][0] < now_in_sec < cls.run_times[cls.day][7]:
                for v in range(7):
                    if cls.run_times[cls.day][v] < now_in_sec < cls.run_times[cls.day][v+1]:
                        cls.ll.log("valve " + str(v) + " = ON")
                        sec_remaining = cls.run_times[cls.day][v+1] - now_in_sec
                        cls.ll.log("sec_remaining " + str(sec_remaining)  + " - " + str(sec_remaining/60)+ "in 7 bit: " + str(2**v))

            cls.relay_board.toggle_led(0)
            cls.update_event.set()
            cls.event.wait(timeout=5)
    # run
