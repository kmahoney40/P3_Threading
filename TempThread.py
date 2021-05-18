import threading
import time
import json
import sys
import requests
from ad_board import ADBoard 
#from Request import Request


# The daqcThread class will read/write the daqc-plate and a relay-plate to monitor temps in and
# outside of the garage and control an exhaust fan.
class daqcThread(threading.Thread):
    def __init__(self, threadID, name, logger, in_dict, event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict
        self.ll = logger
        self.event = event
        self.adc = ADBoard(0, logger, event)
        #self.request = Request('http://192.168.1.106/', logger)

    def raw_to_f(cls, raw):
        # 180.0 * raw - 58 = (100.0 * raw - 50.0) * 1.8 + 32.0
        ret = 180.0 * raw - 58
        return round(ret, 5)


    def run(cls):
        while not cls.event.is_set():
            my_data = { "t1": 0, "t2": 0, "t3": 0, "t4": 0.0, "t5": 0 }

            for t in range(3):
                cls.in_dict[t] = cls.adc.get_adc_filter(t)
            cls.ll.log("Temp Thread")

            my_data["t1"] = cls.raw_to_f(cls.in_dict[0])
            my_data["t2"] = cls.raw_to_f(cls.in_dict[1])
            my_data["t3"] = cls.raw_to_f(cls.in_dict[2])
            my_data["t4"] = 0
            my_data["t5"] = 0

            try:
                newHeaders = {'Content-type': 'application/json'}
                my_json_string = json.dumps(my_data)
                cls.ll.log("my_json_string: " + str(my_json_string), "d")
                ret = requests.post('http://192.168.1.106/temp/temp/', headers=newHeaders, data=my_json_string)
                #ret = cls.request.http_post('temp', newHeaders, my_json_string)
                cls.ll.log("request.http_post() status_code: " + str(ret.status_code), "d")
            except:
                cls.ll.log("TEMP ERROR: " + str(sys.exc_info()[0]), "e")

            cls.event.wait(timeout=900.0)
