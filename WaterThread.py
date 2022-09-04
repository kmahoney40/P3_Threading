import threading
import time
#import request
from datetime import date, datetime, timedelta
from datetime import time
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
    def __init__(self, threadID, name, logger, in_dict, e_quit, is_man_run, is_rain_delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger
        self.in_dict = in_dict
        self.e_quit = e_quit
        self.is_man_run = is_man_run
        self.is_rain_delay = is_rain_delay
        self.previous_man_run = False
        self.pid = self.in_dict['conf']['pid']
        self.relay_board = RelayBoard(self.pid, logger, e_quit)
        #self.request = Request('http://192.168.1.106/', logger)
        self.last_update = 'lastupdate'

        # The days of the week Mon = 0, Tue = 1...
        self.day = datetime.today().weekday()
        self.man_mode = in_dict["man_mode"]
        self.run_times = in_dict["conf"]["run_times"]
        self.in_dict = in_dict
        self.run_today = self.run_times[self.day].copy()
        self.this_run = [[0, 0, 0, 0, 0, 0 , 0, 0], [0, 0, 0, 0, 0, 0 , 0, 0]]
        self.this_run_local = [[0, 0, 0, 0, 0, 0 , 0, 0], [0, 0, 0, 0, 0, 0 , 0, 0]]
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

        self.start_time_as_int = in_dict["conf"]["start_time"]
        self.start_time_local = now# in_dict["conf"]["start_time"]#self.int_time_to_datetime(in_dict["conf"]["start_time"])


        # confJson["start_time"] in 24 hour hhmm
        self.start_time = in_dict["conf"]["start_time"]
        hours = self.start_time // 100
        min = self.start_time - (hours * 100)
        self.start_time = 60 * (hours * 60 + min)
        self.ll.log("confJson.[start_time]: " + str(self.start_time) )
        self.relay_board.set_all_relays(0)
        
    # __init__

    def set_run_today_local(cls, now):
        cls.day = datetime.today().weekday()
        today_times = cls.in_dict["conf"]["run_times"][cls.day].copy()
        today_times = list(map(lambda v: cls.min_to_timedelta(v), today_times))
        
        cls.this_run_local[0] = cls.in_dict["conf"]["run_times"][cls.day].copy()
        cls.this_run_local[0] = list(map(lambda v: cls.start_time_local + cls.min_to_timedelta(v), cls.this_run_local[0]))

        for v in range(1, 8):
            run_min_as_timedelta = cls.this_run_local[0][v-1] + today_times[v]
            cls.this_run_local[0][v] = run_min_as_timedelta

        cls.start_run[0] = cls.start_time_local
        cls.end_run[0] = cls.this_run_local[0][7]

        if not cls.previous_man_run:
            # update this_run[1], manual run only if not actively in man run

            run_min_as_timedelta = (cls.in_dict["conf"]["run_times"][7]).copy()
            cls.this_run_local[1] = (cls.in_dict["conf"]["run_times"][7]).copy()
            cls.this_run_local[1] = list(map(lambda v: now + cls.min_to_timedelta(v), cls.this_run_local[1]))

            for v in range(1,8):
                #run_min_as_timedelta = cls.this_run_local[1][v-1]
                cls.this_run_local[1][v] = cls.in_dict["conf"]["run_times"][7][v-1] + cls.in_dict["conf"]["run_times"][7][v]
                #cls.this_run_local[1][v] = cls.this_run_local[1][v - 1]
            #cls.this_run_local[1] = list(map(lambda v: cls.min_to_timedelta(v) + now, (cls.this_run_local[1]).copy()))
            # cls.ll.log("cls.this_run_local[1]: " + str(cls.this_run_local[1]))

            cls.start_run[1] = now
            cls.end_run[1] = cls.min_to_timedelta(cls.this_run_local[1][7])

        # if cls.is_man_run[0] and not cls.previous_man_run:
        #     # regular run mode
        #     cls.start_run[1] = now
        #     cls.end_run[1] = cls.this_run_local[1][7]
        # cls.ll.log("********************** " + str(cls.end_run[1]) + " ** " + str(cls.this_run_local[1]))
        # if cls.end_run[1] < now:
        #     cls.is_man_run[0] = False 
        # cls.previous_man_run = cls.is_man_run[0]

    # def set_run_today(cls, now_in_sec):
        
    #     cls.ll.log("is_man_run[0]: " + str(cls.is_man_run[0]))

    #     cls.ll.log("cls.run_times: " + str(cls.run_times))

    #     # The days of the week Mon = 0, Tue = 1...
    #     cls.day = datetime.today().weekday()

    #     today_times = cls.run_times[cls.day].copy()

    #     #today_times = list(map(lambda v: v * 60 + cls.start_time, today_times))


    #     cls.this_run[0] = cls.run_times[cls.day].copy()
    #     for v in range(1,8):
    #         cls.this_run[0][v] = (cls.this_run[0][v-1] + today_times[v])
    #     cls.this_run[0] = list(map(lambda v: v * 60 + cls.start_time, cls.this_run[0]))
    #     cls.ll.log("cls.this_run[0]: " + str(cls.this_run[0]))
    #     cls.start_run[0] = cls.start_time
    #     cls.end_run[0] = cls.this_run[0][7]
        
    #     #if not cls.is_man_run[0] and not cls.previous_man_run:
    #     if not cls.previous_man_run:
    #         # update this_run[1], manual run only if not actively in man run
    #         cls.this_run[1] = (cls.in_dict["conf"]["run_times"][7]).copy()
    #         for v in range(1,8):
    #             cls.this_run[1][v] = cls.this_run[1][v-1] + cls.in_dict["conf"]["run_times"][7][v]
    #         cls.this_run[1] = list(map(lambda v: v * 60 + now_in_sec, (cls.this_run[1]).copy()))
    #         cls.ll.log("cls.this_run[1]: " + str(cls.this_run[1]))

    #         cls.start_run[1] = now_in_sec 
    #         cls.end_run[1] = now_in_sec#cls.this_run[1][7]

    #     if cls.is_man_run[0] and not cls.previous_man_run:
    #         # regular run mode
    #         cls.start_run[1] = now_in_sec 
    #         cls.end_run[1] = cls.this_run[1][7]
            
    #     if cls.end_run[1] < now_in_sec:
    #         cls.is_man_run[0] = False 
    #     cls.previous_man_run = cls.is_man_run[0]
        
    #     cls.ll.log("this_run[0]: " + str(cls.this_run[0]), "d")
    #     cls.ll.log("this_run[1]: " + str(cls.this_run[1]), "d")
    #     cls.ll.log("is_man_run[0]: " + str(cls.is_man_run[0]), "d")
    #     cls.ll.log("previous_man_run: " + str(cls.previous_man_run), "d")

    # # set_run_today

    def set_valves(cls, now_in_sec):
        if cls.is_rain_delay[0]:
            cls.relay_board.set_all_relays(0)
            now_in_range = False
        else:

            now_in_sec = datetime.now()
            
            this_run_idx = 1 if cls.is_man_run[0] else 0
            now_in_range = False 
            cls.ll.log("cls.start_run[this_run_idx]: " + str(cls.start_run[this_run_idx]), "d")
            cls.ll.log("now_in_sec: " + str(now_in_sec), "d")
            cls.ll.log("this_run_idx: " + str(this_run_idx), "d")
            cls.ll.log("cls.end_run[this_run_idx]: " + str(cls.end_run[this_run_idx]), "d")

            if cls.start_run[this_run_idx] < now_in_sec < cls.end_run[this_run_idx]:
                now_in_range = True
                for valve in range(7):
                    if cls.this_run_local[this_run_idx][valve] < now_in_sec < cls.this_run_local[this_run_idx][valve+1]:
                        cls.ll.log("valve " + str(valve) + " = ON")
                        cls.in_dict['valve_status'] += 2**valve

                        time_remaining = (cls.this_run_local[this_run_idx][valve+1] - datetime.now())
                        time_remaining_in_sec = time_remaining.seconds
                        cls.ll.log("!!!! time_remaining_in_sec: " + str(time_remaining_in_sec))
                        time_remaining_min = time_remaining_in_sec // 60
                        time_remaining_sec = time_remaining_in_sec - time_remaining_min * 60
                        cls.in_dict["time_remaining"] = str(time_remaining_min).rjust(2, '0') + ":" + str(time_remaining_sec).rjust(2, '0')
                        cls.ll.log("!!!! HH:MM: " + cls.in_dict["time_remaining"])

                        relay = 2**valve
                        cls.relay_board.set_all_relays(relay)
        return now_in_range
    # set_valves    

    def min_to_timedelta(cls, minIn):
        return timedelta(minutes=minIn)

    def int_time_to_datetime(cls, intTime):
        hours_local = intTime // 100
        mins_local = intTime - (hours_local * 100)
        start_time = datetime.now()
        start_time = start_time.replace(hour=hours_local, minute=mins_local, second=0, microsecond=0)
        return start_time

    def midnight_as_datetime():
        dt = date.today()
        return datetime.combine(dt, datetime.min.time())

    def run(cls):

        count = 0
        while not cls.e_quit.is_set():

            #KMDB need to get the date comonent out of cls.start_time_local and others. 
            # it is probalby a datetime timespan would be better. 
            cls.start_time_local = cls.int_time_to_datetime(cls.start_time_as_int)

            now = datetime.now()
            now_in_sec = int((now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds())
            cls.day = datetime.today().weekday()
            
            # Set the current run times, todays times or the manual times
            #cls.set_run_today(now_in_sec)
            cls.set_run_today_local(now)

            #cls.local_start_time = now_in_sec - cls.start_time
            cls.in_dict['valve_status'] = 0
            
            # set_valves does not depend on mode Water or Manual
            if not cls.set_valves(now_in_sec):
                # now_in_sec is outside the min/max run_times, or man_mode just completed - reset to water mode water mode
                cls.send_mail = True
                cls.relay_board.set_all_relays(0)
                cls.ll.log("cls.relay_board.set_all_relays(0) in else")

            cls.ll.log("WATER THREAD" + " threadID: " + str(cls.threadID))


            cls.e_quit.wait(timeout=5.0)
        # while
        cls.relay_board.set_all_relays(0)
    # run
