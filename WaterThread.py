import threading
import time
#import requests
from datetime import datetime
from relay_board import RelayBoard
import logger
import json
#import e_mail
#from Request import Request


# This class will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictionary can be expanded to include weather data that may be used
# to dynamically modify runtimes.
class WaterThread(threading.Thread):
    def __init__(self, threadID, name, logger1, in_dict, e_quit, e_mr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        #self.ll = logger.logger("water")
        #self.ll = logger.logger("WaterThread")
        self.ll = logger1
        self.in_dict = in_dict
        self.e_quit = e_quit
        self.e_mr = e_mr
        self.pid = self.in_dict['conf']['pid']
        self.relay_board = RelayBoard(self.pid, logger1, e_quit)
        #self.log = logger.logger("WaterThread")
        #self.request = Request('http://192.168.1.106/', logger1)

        # The days of the week Mon = 0, Tue = 1...
        self.previous_day = -1
        self.day = datetime.today().weekday()
        self.man_mode = in_dict["man_mode"]
        self.man_times = in_dict["conf"]["man_times"]
        #self.man_run = in_dict["man_run"]
        self.run_times = in_dict["conf"]["run_times"]
        self.start_tm = 0
        self.run_today = self.run_times[self.day].copy()
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

        if cls.in_dict["man_mode"] is 0:
            today_times = cls.run_times[cls.day].copy()
            cls.run_today = cls.run_times[cls.day].copy()
            
            for v in range(1,8):
                cls.run_today[v] = cls.run_today[v-1] + today_times[v]

            cls.run_today = list(map(lambda v: v * 60, cls.run_today))
            cls.ll.log("cls.run_today: " + str(cls.run_today),"d")
            cls.local_start_time = now_in_sec - cls.start_time
            cls.start_tm = cls.start_time
        else:
            today_times = (cls.run_times[cls.day])[:]
            #cls.ll.log("0.1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))
            cls.run_today = cls.man_times.copy()
            #cls.ll.log("1 MANUAL set_run_today cls.man_times: " + str(cls.man_times))

            # do the run min in sec then add in the start time to every element (lambda baby!)
            for v in range(1,8):
                cls.run_today[v] = cls.run_today[v-1] + cls.man_times[v]
            cls.ll.log("1.6 MANUAL set_run_today cls.run_today: " + str(cls.run_today))

            cls.run_today = list(map(lambda v: v * 60, cls.run_today.copy()))

            #emr = "false"
            #if cls.e_mr.is_set():
            #    emr = "true"
            #cls.ll.log("man_run: " + str(cls.in_dict["man_run"]) + " event_man_run: " + emr )
            #if cls.in_dict["man_run"] is not 1:
            if not cls.e_mr.is_set():
                cls.local_start_time = now_in_sec
                cls.start_time = now_in_sec
                cls.ll.log("in_dict[man_run] 1: " + str(cls.in_dict["man_run"]), "d")

        temp_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        cls.run_today = cls.run_today.copy()#temp_list.copy()
        cls.ll.log("SUM run_today: " + str(cls.run_today))
    # set_run_today

    def run(cls):
        #now = datetime.now()
        #cls.mail.send_mail('From WaterThread run()', str(now))
        #cls.mail.send_mail('from WaterThread ctor', str(now))
        while not cls.e_quit.is_set():
            #r = cls.request.http_get('polls/pi')
            #cls.ll.log("Request.http_get(): " + str(r), "d")
            #try:
            #    ret = request.get('polls/pi')
            #   cls.ll.log("requests.get.json(): " + str(ret.text), "d")
            #except Exception as ex:
            #    cls.ll.log("Exception: " + str(ex), 'e')
            #url = 'http://192.168.1.106/water/temp/save'
            #client = requests.session()
            #client.get(url)
            #csrftoken = client.cookies['csrftoken']

            # DELETE needs trailing / in url, get does not.

            #my_data = {login:"somepersonsname", password:"supergreatpassword", csrfmiddlewaretoken:csrftoken}
            
            #r = requests.post('http://192.168.1.106/water/temp/save') 

            #ret = requests.post('http://192.168.1.140/post1', json={'item': 'WOOT'})
            #cls.ll.log("requests.post: " + r.text, "d")

            now = datetime.now()
            now_in_sec = int((now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds())
            cls.day = datetime.today().weekday()
            cls.set_run_today(now_in_sec)
            cls.local_start_time = now_in_sec - cls.start_time
            cls.in_dict['valve_status'] = 0
            cls.ll.log("cls.run_today[0]: " + str(cls.run_today[0]) + " now_in_sec: " + str(now_in_sec) + " cls.run_today[7]: " + str(cls.run_today[7]), "d")
            if cls.run_today[0] < cls.local_start_time < cls.run_today[7]:
                
                #if cls.send_mail:
                #    cls.mail.send_mail('From WaterThread run()', str(now))
                #    cls.send_mail = False
                
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
                        #minn = int((sec_remaining - sec) / 60)
                        relay = 2**v
                        cls.relay_board.set_all_relays(relay)
            else:
                cls.send_mail = True
                cls.relay_board.set_all_relays(0)
                cls.ll.log("cls.relay_board.set_all_relays(0) in else")
                cls.in_dict["man_run"] = 0
                cls.e_mr.clear()
            cls.ll.log("WATER THREAD" + " threadID: " + str(cls.threadID))
            cls.e_quit.wait(timeout=5.0)
        # while
        cls.relay_board.set_all_relays(0)
    # run
