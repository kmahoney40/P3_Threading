import threading
import time
#import request
from datetime import datetime
import enum
from relay_board import RelayBoard
import logger
import json
#import e_mail
from Request import Request


# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class WaterThread(threading.Thread):
    def __init__(self, threadID, name, logger, in_dict, e_quit, e_man_run):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger
        self.in_dict = in_dict
        self.e_quit = e_quit
        self.e_man_run = e_man_run
        self.pid = self.in_dict['conf']['pid']
        self.relay_board = RelayBoard(self.pid, logger, e_quit)
        self.request = Request('http://192.168.1.106/', logger)
        self.last_update = 'lastupdate'

        # The days of the week Mon = 0, Tue = 1...
        self.previous_day = -1
        self.day = datetime.today().weekday()
        self.man_mode = in_dict["man_mode"]
        self.man_times = in_dict["conf"]["man_times"]
        self.man_run = in_dict["man_run"]
        self.run_times = in_dict["conf"]["run_times"]
        self.run_today = self.run_times[self.day].copy()
        self.start_run = 0
        self.end_run = 0
        self.ll.log("in_dict.[start_time]: " + str(in_dict["conf"]["start_time"]))
        self.ll.log("run_today: " + str(self.run_today))

        self.send_mail = True
        #self.mail = e_mail.e_mail()
        # want something like fabs(now - start_time) < 3 sec -> send mail
        now = datetime.now()
        #if(now.minute >= 0)
        #    if (send_mail):
        #self.mail.send_mail('from WaterThread ctor', str(now))
        #        send_mail = False
        #else:
        #    send_mail = True

        # confJson["start_time"] in 24 hour hhmm
        self.start_time = in_dict["conf"]["start_time"]
        hours = self.start_time // 100
        min = self.start_time - (hours * 100)
        self.start_time = 60 * (hours * 60 + min)
        self.local_start_time = self.start_time
        self.ll.log("confJson.[start_time]: " + str(self.start_time) + " local_start_time: " + str(self.local_start_time))
        self.relay_board.set_all_relays(0)
    # __init__

    def set_run_today(cls, now_in_sec):
        # The days of the week Mon = 0, Tue = 1...
        cls.day = datetime.today().weekday()

        if cls.e_man_run.is_set():
            cls.ll.log("@@@@@@@@@@@@ cls.e_man_run     SET: @@@@@@@@@@@@@@@@@@@@")
        else:
            cls.ll.log("@@@@@@@@@@@@ cls.e_man_run NOT SET: @@@@@@@@@@@@@@@@@@@@")

        # not manual 
        if cls.in_dict["man_mode"] is 0:
            today_times = cls.run_times[cls.day].copy()
            cls.run_today = cls.run_times[cls.day].copy()
            
            for v in range(1,8):
                cls.run_today[v] = cls.run_today[v-1] + today_times[v]
            # Convert to seconds
            cls.run_today = list(map(lambda v: v * 60 + cls.start_time, cls.run_today))
            
            cls.start_run = cls.start_time 
            cls.end_run = cls.run_today[7]
            
            cls.ll.log("------------------------- cls.run_today: " + str(cls.run_today),"d")
            cls.ll.log("------------------------- cls.start_run: " + str(cls.start_run),"d")
            cls.ll.log("------------------------- cls.end_run: " + str(cls.end_run),"d")
            cls.local_start_time = now_in_sec - cls.start_time
        else:
            cls.ll.log("0.2 ----------- cls.in_dict['man_run']: " + str(cls.in_dict["man_run"]))

            #if cls.in_dict["man_run"] is 0:
            if not cls.e_man_run.is_set():
                cls.ll.log("0.1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))
            
                cls.run_today = (cls.in_dict["conf"]["man_times"]).copy()# cls.man_times.copy()
                cls.ll.log("1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))
                
                for v in range(1,8):
                    cls.run_today[v] = cls.run_today[v-1] + cls.in_dict["conf"]["man_times"][v]
                cls.ll.log("1.6 MANUAL set_run_today cls.run_today: " + str(cls.run_today))

                # Mult by 60 to get seconds and add now_in_sec KMDB bad doubel add of now_in_sec
                cls.run_today = list(map(lambda v: v * 60 + now_in_sec, cls.run_today.copy()))
                cls.ll.log("1.7 MANUAL set_run_today cls.run_today: " + str(cls.run_today))
                
                cls.local_start_time = now_in_sec
                
                cls.start_run = now_in_sec 

                # now_in_seconds added in cls.run_today
                cls.end_run = cls.run_today[7]
                
                cls.ll.log("cls.man_run: ", "d")
            elif cls.end_run < now_in_sec:
                cls.in_dict["man_run"] = 0
                cls.e_man_run.clear()
                cls.in_dict["man_mode"] = 0

        cls.ll.log("SUM run_today: " + str(cls.run_today))
    # set_run_today

    def set_valves(cls, now_in_sec):
        now_in_range = False
        if cls.start_run < now_in_sec < cls.end_run:
            now_in_range = True
            for valve in range(7):
                cls.ll.log("^^^^^^^^ : cls.run_today[valve]: " + str(cls.run_today[valve]))
                cls.ll.log("^^^^^^^^ : now_in_sec" + str(now_in_sec))
                cls.ll.log("^^^^^^^^ : cls.run_today[valve+1]: " + str(cls.run_today[valve+1]))
                
                if cls.run_today[valve] < now_in_sec < cls.run_today[valve+1]:
                    cls.ll.log("valve " + str(valve) + " = ON")
                    cls.in_dict['valve_status'] += 2**valve
                    sec_remaining = cls.run_today[valve+1] - now_in_sec
                    sec = sec_remaining % 60

                    remaining_sec = sec_remaining % 60
                    remaining_min = int((sec_remaining - sec) / 60)
                    time_remaining_str = str(remaining_min).zfill(2) + ":" + str(remaining_sec).zfill(2)
                    cls.in_dict["time_remaining"] = time_remaining_str
                    cls.ll.log("++++++++++++++++++++++++++++++ time_remaining str: " + time_remaining_str)
                    cls.ll.log("sec: " + str(sec))
                    relay = 2**valve
                    cls.relay_board.set_all_relays(relay)
        return now_in_range
    # set_valves    

    def run(cls):
        while not cls.e_quit.is_set():

            cls.ll.log("KMDB ++++++++++++++++ in_dict[man_mode]: " + str(cls.in_dict["man_mode"]), "d")
            cls.ll.log("KMDB ++++++++++++++++  in_dict[man_run]: " + str(cls.in_dict["man_run"]), "d")
            cls.ll.log("KMDB ****************       cls.man_run: " + str(cls.man_run), "d")

            cls.ll.log("cls.in_dict: " + str(cls.in_dict), "d")
            cls.ll.log("cls.in_dict[man_times]: " + str(cls.in_dict["conf"]["man_times"]), "d")
            cls.ll.log("cls.in_dict[run_times]: " + str(cls.in_dict["conf"]["run_times"]), "d")

            now = datetime.now()
            now_in_sec = int((now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds())
            cls.day = datetime.today().weekday()
            
            # Set the current run times, todays times or the manual times
            cls.set_run_today(now_in_sec)
            
            cls.local_start_time = now_in_sec - cls.start_time
            cls.in_dict['valve_status'] = 0
            cls.ll.log("cls.run_today[0]: " + str(cls.run_today[0]) + " now_in_sec: " + str(now_in_sec) + " cls.run_today[7]: " + str(cls.run_today[7]), "d")

            cls.ll.log("cls.run_today[0] < now_in_sec < cls.run_today[7]", "d")
            cls.ll.log("@@@@@@@@@@@ cls.start_run: " + str(cls.start_run), "d")
            cls.ll.log("&&&&&&&&&&& cls.end_run: " + str(cls.end_run), "d")
            cls.ll.log("$$$$$$$$$$$ now_in_sec: " + str(now_in_sec), "d")
            cls.ll.log("@@@@@@@@@@@ cls.run_today[0]: " + str(cls.run_today[0]), "d")
            cls.ll.log("&&&&&&&&&&& cls.run_today[7]: " + str(cls.run_today[7]), "d")
            
            # set_valves does not depend on mode Water or Manual
            if not cls.set_valves(now_in_sec):
                # now_in_sec is outside the min/max run_times, or man_mode just completed - reset to water mode water mode
                cls.send_mail = True
                cls.relay_board.set_all_relays(0)
                cls.ll.log("cls.relay_board.set_all_relays(0) in else")
                if cls.in_dict["man_mode"] is 1 and  now_in_sec > cls.end_run:
                    cls.in_dict["man_mode"] = 0
                    cls.in_dict["man_run"] = 0
                    cls.e_man_run.clear()
                    cls.local_start_time = now_in_sec - cls.start_time

            cls.ll.log("WATER THREAD" + " threadID: " + str(cls.threadID))

            # pause loop
            cls.e_quit.wait(timeout=5.0)
        # while
        cls.relay_board.set_all_relays(0)
    # run
