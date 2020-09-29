import threading
import time
from datetime import datetime
from relay_board import RelayBoard
import logger
import json

# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class WaterThread(threading.Thread):
    def __init__(self, threadID, name, in_dict, event, update_event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger.logger("water")
        self.in_dict = in_dict
        self.event = event
        self.update_event = update_event
        self.pid = self.in_dict['conf']['pid']
        self.relay_board = RelayBoard(self.pid, event)

        # The days of the week Mon = 0, Tue = 1...
        self.previous_day = -1
        self.day = datetime.today().weekday()
        # Read conf file
        #confFile = open("irrigation.conf", "r")
        #confData = confFile.read()
        #confJson = json.loads(confData)
        #self.ll.log("confJson: " + str(confJson))
        self.man_mode = in_dict["man_mode"]
        self.man_times = in_dict["conf"]["man_times"]
        #self.man_run = in_dict["man_run"]
        self.run_times = in_dict["conf"]["run_times"]
        self.start_tm = 0
        self.run_today = self.run_times[self.day].copy()
        self.ll.log("in_dict.[start_time]: " + str(in_dict["conf"]["start_time"]))
        self.ll.log("run_today: " + str(self.run_today))
        
        # confJson["start_time"] in 24 hour hhmm
        self.start_time = in_dict["conf"]["start_time"]
        hours = self.start_time // 100
        min = self.start_time - (hours * 100)
        self.start_time = 60 * (hours * 60 + min)
        self.local_start_time = self.start_time
        self.ll.log("confJson.[start_time]: " + str(self.start_time) + " local_start_time: " + str(self.local_start_time))

        #for v in range(1,8):
        #    self.run_today[v] += self.run_today[v-1]
        #self.ll.log("SUM run_today: " + str(self.run_today))
        
        #for v in range(8):
        #    self.ll.log("BEFORE run_today[v]: " + str(self.run_today[v]))
            # use a map here (lambda)
        #    self.run_today[v] = (self.run_today[v] * 60) + self.start_time
        #    self.ll.log("AFTER  run_today[v]: " + str(self.run_today[v]))
            
        self.relay_board.set_all_relays(0)
    # __init__

    def set_run_today(cls, now_in_sec):
        #start_tm = 0
        # The days of the week Mon = 0, Tue = 1...
        cls.day = datetime.today().weekday()
        #cls.run_today = cls.run_times[cls.day]

        cls.ll.log("man_times[]: " + str(cls.man_times), "d")
        cls.ll.log("in_dict[man_mode]: " + str(cls.in_dict["man_mode"]),"d")

        cls.ll.log("0 in_dict[man_run]: " + str(cls.in_dict["man_run"]), "d")

        if cls.in_dict["man_mode"] is 0:
            today_times = cls.run_times[cls.day].copy()
            cls.run_today = cls.run_times[cls.day].copy()
            
            cls.ll.log("0 STANDARD set_run_today cls.run_today: " + str(cls.run_today))
            for v in range(1,8):
                cls.run_today[v] = cls.run_today[v-1] + today_times[v]
            cls.ll.log("1 STANDARD set_run_today cls.run_today: " + str(cls.run_today))

            cls.run_today = list(map(lambda v: v * 60, cls.run_today))
            cls.ll.log("cls.run_today: " + str(cls.run_today),"d")
            # cls.start_time is in seconds
            cls.local_start_time = now_in_sec - cls.start_time
            cls.start_tm = cls.start_time
        else:
            today_times = (cls.run_times[cls.day])[:]
            cls.ll.log("0.1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))
        #if cls.in_dict["man_run"] is not 1:
            cls.run_today = cls.man_times.copy()
            #start_tm = now_in_sec
            #now_in_sec *= 1
            cls.ll.log("1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))

            # do the run min in sec then add in the start time to every element (lambda baby!)
            cls.ll.log("1.5 MANUAL set_run_today cls.run_today: " + str(cls.man_times))
            for v in range(1,8):
                cls.run_today[v] = cls.run_today[v-1] + cls.man_times[v]
            cls.ll.log("1.6 MANUAL set_run_today cls.run_today: " + str(cls.run_today))

            cls.run_today = list(map(lambda v: v * 60, cls.run_today.copy()))

            cls.ll.log("2 MANUAL now_in_sec: " + str(now_in_sec))
            cls.ll.log("2 MANUAL set_run_today cls.run_today: " + str(cls.run_today))
            cls.ll.log("in_dict[man_run] 0: " + str(cls.in_dict["man_run"]), "d")
            if cls.in_dict["man_run"] is not 1:
                cls.local_start_time = now_in_sec
                cls.start_time = now_in_sec
                #cls.in_dict["man_run"] = 0
                cls.ll.log("in_dict[man_run] 1: " + str(cls.in_dict["man_run"]), "d")

        cls.ll.log("0 start_tm: " + str(cls.start_tm))
        temp_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        cls.run_today = cls.run_today.copy()#temp_list.copy()
        cls.ll.log("SUM run_today: " + str(cls.run_today))
    # set_run_today

    def run(cls):
        while not cls.event.is_set():
            rl = logger.logger("water run")
            rl.log("WOOT")
            now = datetime.now()
            now_in_sec = int((now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds())
            cls.ll.log("now_in_sec: " + str(now_in_sec))
            cls.day = datetime.today().weekday()
            cls.ll.log("day: " + str(cls.day))
            cls.ll.log("cls.run_today[0] " + str(cls.run_today[0]))
            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]))

            cls.ll.log("BEFORE *** cls.run_today[] " + str(cls.run_today), "d")
            cls.ll.log("cls.day " + str(cls.day) + " cls.previous_day " + str(cls.previous_day), "d")
            cls.set_run_today(now_in_sec)
            cls.ll.log("run() AFTER ***cls.run_today[] " + str(cls.run_today), "d")

            cls.local_start_time = now_in_sec - cls.start_time
            cls.ll.log("cls.local_start_time: " + str(cls.local_start_time), "d")
            cls.in_dict['valve_status'] = 0
            cls.ll.log("cls.run_today[0]: " + str(cls.run_today[0]) + " now_in_sec: " + str(now_in_sec) + " cls.run_today[7]: " + str(cls.run_today[7]), "d")
            if cls.run_today[0] < cls.local_start_time < cls.run_today[7]:
                cls.ll.log("cls.run_today[0] < now_in_sec < cls.run_today[7]", "d")
                for v in range(7):
                    if cls.run_today[v] < cls.local_start_time < cls.run_today[v+1]:
                        cls.ll.log("valve " + str(v) + " = ON")
                        cls.in_dict['valve_status'] += 2**v
                        sec_remaining = cls.run_today[v+1] - cls.local_start_time# - now_in_sec
                        sec = sec_remaining % 60

                        remaining_sec = sec_remaining % 60
                        remaining_min = int((sec_remaining - sec) / 60)
                        time_remaining_str = str(remaining_min).zfill(2) + ":" + str(remaining_sec).zfill(2)
                        cls.in_dict["time_remaining"] = time_remaining_str
                        cls.ll.log("time_remaining str: " + time_remaining_str)
                        cls.ll.log("sec: " + str(sec))
                        minn = int((sec_remaining - sec) / 60)
                        cls.ll.log("sec_remaining " + str(sec_remaining)  + " - " + str(sec_remaining/60)+ " in 7 bit: " + str(2**v))
                        time_remaining = datetime.fromtimestamp(sec_remaining)
                        cls.ll.log("time remianing: " + str(time_remaining))
                        cls.ll.log("time remaining min sec: " + str(minn) + ":" + str(sec).zfill(2))
                        relay = 2**v
                        cls.relay_board.set_all_relays(relay)
                        cls.ll.log("SPRINKLER DICT[0]: " + str(cls.in_dict['valve_status']))
                    else:
                        cls.relay_board.set_all_relays(0)
                        cls.ll.log("CLEAR ALL RELAYS: " + str(v))
            else:
                cls.in_dict["man_run"] = 0
            cls.ll.log("SPRINKLER DICT[0]: " + str(cls.in_dict['valve_status']))

            cls.update_event.set()
            cls.event.wait(timeout=5)
    # run
