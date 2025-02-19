import threading
import time
#import request
from datetime import datetime, timedelta
import enum
from relay_board import RelayBoard
import logger
import json
#import e_mail
#from Request import Request


# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class WaterThread(threading.Thread):
    def __init__(self, threadID, name, logger, in_dict, e_quit, is_man_run, tomorrow_in_sec, delay_in_sec, e_garage_door, e_stop_water_thread):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger
        self.in_dict = in_dict
        self.e_quit = e_quit
        self.e_garage_door = e_garage_door
        self.e_stop_water_thread = e_stop_water_thread
        self.is_man_run = is_man_run
        self.tomorrow_in_sec = tomorrow_in_sec
        self.delay_in_sec = delay_in_sec
        self.previous_man_run = False
        self.pid = self.in_dict['conf']['pid']
        self.relay_board = RelayBoard(self.pid, logger, e_quit)
        self.second_board = RelayBoard(self.pid + 1, logger, e_quit)
        #self.request = Request('http://192.168.1.106/', logger)
        self.last_update = 'lastupdate'

        # The days of the week Mon = 0, Tue = 1...
        self.previous_day = -1
        self.day = datetime.today().weekday()
        self.man_mode = in_dict["man_mode"]
        #self.man_times = in_dict["conf"]["man_times"]
        #self.man_run = in_dict["man_run"]
        self.run_times = in_dict["conf"]["run_times"]
        self.run_today = self.run_times[self.day].copy()
        self.this_run = [[0, 0, 0, 0, 0, 0 , 0, 0], [0, 0, 0, 0, 0, 0 , 0, 0]]
        self.start_run = [0, 0]
        self.end_run = [0, 0]
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
        #self.local_start_time = self.start_time
        self.ll.log("confJson.[start_time]: " + str(self.start_time) )#+ " local_start_time: " + str(self.local_start_time))
        self.relay_board.set_all_relays(0)
        self.second_board.set_all_relays(0)
    # __init__

    def set_run_today(cls, now_in_sec):
        
        cls.ll.log("----------------- cls.tomorrow_in_sec[0]: " + str(cls.tomorrow_in_sec[0]))
        now = datetime.now()
        cls.ll.log("----------------- now " + str(now))

        if cls.tomorrow_in_sec[0] > 0:
            # Get today's date and time
            # Calculate the date for the day after tomorrow
            day_after_tomorrow = now + timedelta(days=2)
            cls.ll.log("----------------- day_after_tomorrow " + str(day_after_tomorrow))
            # Create a new datetime object for 00:00:00 that day
            midnight_day_after_tomorrow = datetime(day_after_tomorrow.year, day_after_tomorrow.month, day_after_tomorrow.day)
            cls.ll.log("----------------- midnight_day_after_tomorrow " + str(midnight_day_after_tomorrow))
            
            if now > midnight_day_after_tomorrow:
                cls.tomorrow_in_sec[0] = 0
            else:
                cls.ll.log("----------------- water off until " + str(midnight_day_after_tomorrow))
                return

        
        # if now_in_sec < cls.tomorrow_in_sec[0]:
        #     cls.this_run = [[0, 0, 0, 0, 0, 0 , 0, 0], [0, 0, 0, 0, 0, 0 , 0, 0]]
            
        #     cls.ll.log("----------------- cls.tomorrow_in_sec[0]: " + str(cls.tomorrow_in_sec[0]))
        #     cls.ll.log("----------------- now_in_sec: " + str(now_in_sec))
        #     cls.ll.log("----------------- cls.delay_in_sec[0]: " + str(cls.delay_in_sec[0]))
        #     cls.ll.log("----------------- cls.tomorrow_in_sec[0]: " + str(cls.tomorrow_in_sec[0]))
        #     cls.ll.log("----------------- now_in_sec: " + str(now_in_sec))
        #     cls.ll.log("----------------- cls.delay_in_sec[0]: " + str(cls.delay_in_sec[0]))
            
        #     cls.delay_in_sec[0] = cls.tomorrow_in_sec[0] - now_in_sec
        #     if cls.delay_in_sec[0] < 0:
        #         cls.delay_in_sec[0] = 0
        #     #cls.ll.log("now_in_sec: " + str(now_in_sec))
        #     #cls.ll.log("tomorrow_in_sec[0]: " + str(cls.tomorrow_in_sec[0]))
        #     return
        
        # if cls.tomorrow_in_sec[0] > 0:
        #     cls.tomorrow_in_sec[0] = 0
        #     cls.ll.log("tomorrow_in_sec[0]: " + str(cls.tomorrow_in_sec[0]))
        
        cls.ll.log("is_man_run[0]: " + str(cls.is_man_run[0]))

        
        # The days of the week Mon = 0, Tue = 1...
        cls.day = datetime.today().weekday()

        today_times = cls.run_times[cls.day].copy()
        cls.this_run[0] = cls.run_times[cls.day].copy()
        for v in range(1,8):
            cls.this_run[0][v] = (cls.this_run[0][v-1] + today_times[v])
        cls.this_run[0] = list(map(lambda v: v * 60 + cls.start_time, cls.this_run[0]))
        cls.ll.log("cls.this_run[0]: " + str(cls.this_run[0]))
        cls.start_run[0] = cls.start_time
        cls.end_run[0] = cls.this_run[0][7]
        
        #if not cls.is_man_run[0] and not cls.previous_man_run:
        if not cls.previous_man_run:
            # update this_run[1], manual run only if not actively in man run
            cls.this_run[1] = (cls.in_dict["conf"]["run_times"][7]).copy()
            for v in range(1,8):
                cls.this_run[1][v] = cls.this_run[1][v-1] + cls.in_dict["conf"]["run_times"][7][v]
            cls.this_run[1] = list(map(lambda v: v * 60 + now_in_sec, (cls.this_run[1]).copy()))
            cls.ll.log("cls.this_run[1]: " + str(cls.this_run[1]))

            cls.start_run[1] = now_in_sec 
            cls.end_run[1] = now_in_sec#cls.this_run[1][7]

        if cls.is_man_run[0] and not cls.previous_man_run:            
            # regular run mode
            cls.start_run[1] = now_in_sec 
            cls.end_run[1] = cls.this_run[1][7]
            
        if cls.end_run[1] < now_in_sec:
            cls.is_man_run[0] = False 
        cls.previous_man_run = cls.is_man_run[0]
        
        cls.ll.log("this_run[0]: " + str(cls.this_run[0]), "d")
        cls.ll.log("this_run[1]: " + str(cls.this_run[1]), "d")
        cls.ll.log("is_man_run[0]: " + str(cls.is_man_run[0]), "d")
        cls.ll.log("previous_man_run: " + str(cls.previous_man_run), "d")

    # set_run_today

    def set_valves(cls, now_in_sec):
        this_run_idx = 1 if cls.is_man_run[0] else 0 # ?: operator in C#
        now_in_range = False 
        cls.ll.log("cls.start_run[this_run_idx]: " + str(cls.start_run[this_run_idx]), "d")
        cls.ll.log("now_in_sec: " + str(now_in_sec), "d")
        cls.ll.log("cls.end_run[this_run_idx]: " + str(cls.end_run[this_run_idx]), "d")
        cls.ll.log("this_run_idx: " + str(this_run_idx), "d")
        if cls.start_run[this_run_idx] < now_in_sec < cls.end_run[this_run_idx]:
            now_in_range = True
            for valve in range(7):
                if cls.this_run[this_run_idx][valve] < now_in_sec < cls.this_run[this_run_idx][valve+1]:
                    cls.ll.log("valve " + str(valve) + " = ON")
                    cls.in_dict['valve_status'] += 2**valve
                    sec_remaining = cls.this_run[this_run_idx][valve+1] - now_in_sec
                    cls.ll.log("@@@@ sec_remaining: " + str(sec_remaining))
                    sec = sec_remaining % 60

                    remaining_sec = sec_remaining % 60
                    remaining_min = int((sec_remaining - sec) / 60)
                    cls.ll.log("@@@@ remaining_min: " + str(remaining_min))
                    time_remaining_str = str(remaining_min).zfill(2) + ":" + str(remaining_sec).zfill(2)
                    cls.in_dict["time_remaining"] = time_remaining_str
                    relay = 2**valve
                    cls.relay_board.set_all_relays(relay)
        return now_in_range
    # set_valves    

    def run(cls):
        while not cls.e_quit.is_set() and not cls.e_stop_water_thread.is_set():

            cls.ll.log("WATER THREAD" + " threadID: " + "WATER THREAD IS RUNNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            cls.ll.log("WATER THREAD" + " run_times: " + str(cls.run_times))

            now = datetime.now()
            now_in_sec = int((now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds())
            cls.day = datetime.today().weekday()
            
            # Set the current run times, todays times or the manual times
            #if now > 24hour_delay default to 00:00:00
            cls.set_run_today(now_in_sec)
            
            #cls.local_start_time = now_in_sec - cls.start_time
            cls.in_dict['valve_status'] = 0
            
            #KMDB move this to a function, or another file, maybe a class
            if cls.e_garage_door.is_set():
                cls.second_board.relay_on(5)
                cls.ll.log("cls.second_board.relay_on(2) in if")


            # if now < 24hourdelay, then set all valves to off
            # else
            # if now > 24hourdelay, then set set 24hourdelay 00:00:00 and run set_valves
            # in main 24hourdelay = datetime.now() + timedelta(days=1)
            # to reset the 24hourdelay use 00:00:00 24hourdelay = datetime.combine(date.today(), datetime.min.time())
            
            # set_valves does not depend on mode Water or Manual
            if not cls.set_valves(now_in_sec):
                # now_in_sec is outside the min/max run_times, or man_mode just completed - reset to water mode water mode
                cls.send_mail = True
                cls.relay_board.set_all_relays(0)
                cls.ll.log("cls.relay_board.set_all_relays(0) in else")

            cls.ll.log("WATER THREAD" + " threadID: " + str(cls.threadID))

            if cls.e_garage_door.is_set():
                cls.ll.log("cls.e_garage_door.is_set")
                cls.e_quit.wait(timeout=1.0)
                cls.ll.log("cls.e_garage_door.is_set AFTER 1 sec wait")
                cls.second_board.relay_off(5)
                cls.e_garage_door.clear()
                cls.ll.log("cls.e_garage_door.clear()")
                #cls.e_quit.set()
            else:
                # pause loop
                cls.e_quit.wait(timeout=5.0)
        # while
        cls.relay_board.set_all_relays(0)
    # run
