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
        self.relay_board = RelayBoard(1, event)
        self.pid = self.in_dict['conf']['pid']

        # The days of the week Mon = 0, Tue = 1...
        self.day = datetime.today().weekday()
        
        # Read conf file
        confFile = open("irrigation.conf", "r")
        confData = confFile.read()
        confJson = json.loads(confData)
        self.ll.log("confJson: " + str(confJson))
        self.run_times = confJson["run_times"]
        self.run_today = self.run_times[self.day]
        self.ll.log("confJson.[start_time]: " + str(confJson["start_time"]))
        self.ll.log("run_today: " + str(self.run_today))
        
        self.start_time = confJson["start_time"]# * 60 * 60
        hours = self.start_time // 100
        min = self.start_time - (hours * 100)
        self.start_time = 60 * (hours * 60 + min)
        self.ll.log("confJson.[start_time]: " + str(self.start_time))
        
        for v in range(1,8):
            self.run_today[v] += self.run_today[v-1]
        self.ll.log("SUM run_today: " + str(self.run_today))
        
        for v in range(8):
            self.ll.log("BEFORE run_today[v]: " + str(self.run_today[v]))
            # use a map here (lambda)
            self.run_today[v] = (self.run_today[v] * 60) + self.start_time
            self.ll.log("AFTER  run_today[v]: " + str(self.run_today[v]))
            
        self.relay_board.set_all_relays(0)
        
        self.ct = 0
        
        
    # __init__
    
    def run(cls):
        while not cls.event.is_set():
            rl = logger.logger("water run")
            rl.log("WOOT")
            now = datetime.now()
            now_in_sec = (now - now.replace(hour=0, minute=0, second=0,microsecond=0)).total_seconds()
            cls.ll.log("now_in_sec: " + str(now_in_sec))
            cls.day = datetime.today().weekday()
            cls.ll.log("day: " + str(cls.day))
            cls.ll.log("cls.run_today[0] " + str(cls.run_today[0]))
            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]))

            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]), "i")
            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]), "w")
            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]), "e")
            cls.ll.log("cls.run_today[7] " + str(cls.run_today[7]), "d")

            cls.in_dict['valve_status'] = 0
            if cls.run_today[0] < now_in_sec < cls.run_today[7]:
                for v in range(7):
                    if cls.run_today[v] < now_in_sec < cls.run_today[v+1]:
                        cls.ll.log("valve " + str(v) + " = ON")
                        cls.in_dict['valve_status'] += 2**v
                        sec_remaining = cls.run_today[v+1] - now_in_sec
                        #time_remaining = str(datetime.timedelta(sec_remaining)) 
                        # call relayALL(csl.in_dict[0])
                        cls.ll.log("sec_remaining " + str(sec_remaining)  + " - " + str(sec_remaining/60)+ "in 7 bit: " + str(2**v))
                        #cls.ll.log("time_remaining " + time_remaining)
                        cls.ll.log("SPRINKLER DICT[0]: " + str(cls.in_dict['valve_status']))
                    else:
                        cls.relay_board.set_all_relays(0)
            cls.ll.log("SPRINKLER DICT[0]: " + str(cls.in_dict['valve_status']))

            #ct = 0
            """
            if cls.ct == 1:
                cls.ll.log("BEFORE relay_on")
                #cls.relay_board.relay_on(1)
                cls.relay_board.set_all_relays(1)
                #cls.relay_board.relay_toggle(1)
                cls.relay_board.led_toggle()
                cls.ll.log("AFTER relay_on")
            if cls.ct == 2:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(2)
                cls.relay_board.set_all_relays(1)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            if cls.ct == 3:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(3)
                cls.relay_board.set_all_relays(4)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            if cls.ct == 4:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(4)
                cls.relay_board.set_all_relays(8)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            if cls.ct == 5:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(5)
                cls.relay_board.set_all_relays(16)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            if cls.ct == 6:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(6)
                cls.relay_board.set_all_relays(32)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            if cls.ct == 7:
                cls.ll.log("2-BEFORE relay_onf")
                #cls.relay_board.relay_off(7)
                cls.relay_board.set_all_relays(64)
                cls.relay_board.led_toggle()
                cls.ll.log("2-AFTER relay_off")
            """
            state = cls.relay_board.get_relay_state()
            cls.ll.log("ct = " + str(cls.ct) + " state = " + str(state))
            #cls.in_dict["valve_status"] = state
            """
            if cls.ct > 0:
                mask = 1 << cls.ct - 1
                v = state & mask
                cls.ll.log("mask: " + str(mask) + " v: " + str(v))
            """
            cls.ct += 1
            
            if cls.ct > 7:
                cls.ct = 0
            cls.update_event.set()
            cls.event.wait(timeout=5)
    # run
