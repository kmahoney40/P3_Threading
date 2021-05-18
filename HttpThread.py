import threading
import time
import sys
import datetime
from relay_board import RelayBoard
import requests
import logger
import json

class HttpThread(threading.Thread):
    def __init__(self, threadID, name, logger1, in_dict, e_quit):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ll = logger1
        self.in_dict = in_dict
        self.e_quit = e_quit
        self.last_updated = datetime.datetime.now() - datetime.timedelta(days=3560)

    def run(cls):
        while not cls.e_quit.is_set():
            cls.ll.log("HTTP THREAD last_updated: " + str(cls.last_updated))

#            try:
#                rta = requests.get('http://192.168.1.106/temp/runtimesaudit/1')
#                if rta.status_code == 200:
#                    js = rta.json()
#                    #cls.ll.log("HTTP THREAD js: " + js, "d")
#                    jss = str(js)
#                    #j_jss = json.load(jss)
#                    cls.ll.log("HTTP THREAD rta: " + str(rta.json()), "d")
#                    cls.ll.log("HTTP THREAD jss: " + jss, "d")
#                    
#                    #last_update_time = json.loads(str(rta.json)).decode('utf-8')#['date_modified']
#                    #lutj = last_update_time['date_modified']
#                    last_update_time = json.dumps(rta.json())
#                    cls.ll.log("HTTP THREAD datetime.now: " + last_update_time, "d")
#                    
#                    cls.ll.log("HTTP THREAD datetime.now: " + str(datetime.datetime.now()), "d")
#
#                    str2 = '{"id": 1, "date_modified": "2021-03-06T14:18:50-08:00"}'
#                    str22 = json.loads(last_update_time)
#                    vvv = str22["date_modified"]
#                    cls.ll.log("HTTP THREAD vvv: " + str(vvv), "d")
#                    date_time_obj = datetime.datetime.strptime(vvv)
#                    
#                    if cls.last_updated < date_time_obj:
#                        cls.ll.log("HTTP THREAD update cls.last_updatde: " + str(datetime.datetime.now()), "d")
#                        
#                    
#                #ret = requests.get('http://192.168.1.106/temp/runtimes')
#
#                #if ret.status_code == 200:
#                #    cls.ll.log("HTTP THREAD ret: " + str(ret.json()), "d")
#                    
#            except:
#                cls.ll.log("HTTP THREAD ERROR: " + str(sys.exc_info()[0]), "e")
              

            cls.e_quit.wait(timeout=5.0)
