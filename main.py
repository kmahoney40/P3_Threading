import threading
from datetime import datetime
import time
import curses
import sys
import json
import ConfFile
import WaterThread
import TempThread
import HttpThread
import logger
from Request import Request
from flask import Flask, request, jsonify
from werkzeug.serving import make_server


# These will become JSON
#water_dict = [0, {"start_time": 600}]
water_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", 
                "conf": {
                    "start_time": 600,
                    "pid": 0,
                    "alpha": 0.075,
                    "log_level": "DEBUG",
                    "run_times": [
                        [0,  10, 15,  0,  0, 15, 15, 10],
                        [10, 10, 10,  0, 45, 10, 10, 10],
                        [0,  10, 15,  0,  0, 15, 15, 10],
                        [10,  0,  0,  0,  0,  0,  0,  0],
                        [5, 5,  0,  0,  0, 15, 0,  5],
                        [0,  0, 15,  0, 45,  0,  0,  0],
                        [0, 10,  0,  5,  0,  5,  5,  0],
                        [0, 0, 0, 0, 0, 0, 0, 0]
                    ]
                }
            }

daqc_dict = [0,0,0,0,0,0,0,0]
days = ["Mon ", "Tue ", "Wed ", "Th  ", "Fri ", "Sat ", "Sun "]
mode = ["Water"]
e_mode = ""
is_man_run = [False]
last_key = ['a']
last_successful_update = [datetime.now()]

#man_run = False
run_times = ["", "", "", "", "", "", ""]
disp_run_times = []
day = [0] #0 - 6 for day of week
man_value = 0 #0 - 6 for valve to manually run

#KMDB use this to stop the water thread when the web server has updated the run times. When water thread is stopped the irrigation.conf file is updated
# then the water thread is restarted with the new run times.
event_stop_water_thread = threading.Event()


updateCounter = [0]
newVal = [0]

def display_head(win, logger, mode):
    try:
        now = datetime.now()
        now_formated = now.strftime("%m/%d/%Y, %H:%M:%S")#datetime.now()
        win.addstr(0, 0, "Now: " +  now_formated + "   Mode: " + mode + " Auto Start Time: " + str(water_dict["conf"]["start_time"]))
        win.clrtoeol()
    except:
        logger.log("Error in display_head: " + str(sys.exc_info()[0]))
# display_head

def display_body(win, logger):
    try:
        win.addstr(0, 0, "Start Time: " + str(water_dict["conf"]["start_time"]))
        num_runs = len(water_dict["conf"]["run_times"])
        num_valves = 7

        for valve in range(num_valves):
            mask = 1 << valve
            state = water_dict["valve_status"] & mask
            on_off = "OFF"
            if state:
                on_off = "ON  Reamaining: " + water_dict["time_remaining"]
            win.addstr(0 + valve, 0, "Valve " + str(valve+1) + " state: " + on_off)
            win.clrtoeol()

        for run in range(num_runs - 1):
            win.addstr(0 + run, 43, days[run])
            for valve in range(1, num_valves + 1):
                win.addstr(0 + run, 41 + 4 + valve*4, str(water_dict["conf"]["run_times"][run][valve]).rjust(2))
            win.clrtoeol()

        win.addstr(8, 0, "Up: 'a' 's' 'd' 'f' 'g' 'h' 'j'")
        # man_times length is 8, extra is used in calculations in WaterThread
        for v in range(1,len(water_dict['conf']['run_times'][7])):
            win.addstr(9, 3 + (v-1)*4, str(water_dict['conf']['run_times'][7][v]).rjust(3))
        win.addstr(10, 0, "Dn: 'z' 'x' 'c' 'v' 'b' 'n' 'm'")
        
        win.addstr(12, 0, "Up:        '4' '5' '6' '7' '8' '9' '0'")
        win.addstr(13, 0, "Day: " + days[day[0]] + "-")
        win.clrtoeol()
        for v in range(1,len(water_dict['conf']['run_times'][0])):
            win.addstr(13, 10 + (v-1)*4, str(water_dict['conf']['run_times'][day[0]][v]).rjust(3))
        win.addstr(14, 0, "Dn:        'f' 'g' 'h' 'j' 'k' 'l' ';'")

        logger.log("water_dict['conf']['run_times'][7]: " + str(water_dict['conf']['run_times'][7]))
    except:
        logger.log("Error in display_body: " + str(sys.exc_info()[0]))
# display_body

def display2_body(win, logger):
    try:
        logger.log("display2_body: " + str(sys.exc_info()[0]), "d")
    except:
        logger.log("Error in display2_body: " + str(sys.exc_info()[0]), "e")

def display_foot(win, logger):
    try:
        win.addstr(0, 0, "Footer line 1", curses.A_UNDERLINE)
        win.addstr(1, 0, "FooterLine 2", curses.A_UNDERLINE)
    except:
        logger.log("Error in display_foot: " + str(sys.exc_info()[0]))
# display_foot


def adj_run_times(inCh, logger, water_dict):
    d_time = 1
    idx = 0
    ret_tuple = (0,0,0)
    valid_key_press = ['4', '5', '6', '7', '8', '9', '0', '$', '%', '^', '&', '*', '(',')', 'f','g','h','j','k','l', ';', 'F', 'G', 'H', 'J', 'K', 'L', ':', '-', '+']
    if inCh in valid_key_press:
        idx = valid_key_press.index(inCh)
        if inCh == '-':
            day[0] = (day[0] - 1) % 7
        if inCh == '+':
            day[0] = (day[0] + 1) % 7
        if inCh.isupper() or inCh in ['$', '%', '^', '&', '*', '(', ')', ':']:
            d_time = 5
        if idx > 13 and idx < 28:
            d_time *= -1
        idx = (idx % 7) + 1
        ret_tuple = (day[0],idx,d_time)
        
    return ret_tuple

def adj_man_time(inCh, logger):
    
    d_time = 1
    idx = 0
    ret_tuple = (0,0)

    logger.log("OUTSIDE adj_man_times inCh: " + str(inCh), "d")

    valid_key_press = ['a','s','d','f','g','h','j','A','S','D','F','G','H','J','z','x','c','v','b','n','m','Z','X','C','V','B','N','M']
    if inCh in valid_key_press:
        logger.log("INSIDE adj_man_times inCh: " + str(inCh), "d")
        # idx is for a  v and we want to skip the 1st element, as the frist element of run_times is not actually a ru time
        idx = valid_key_press.index(inCh)
        if inCh.isupper():
            d_time = 5
        if idx > 13:
            d_time *= -1
        logger.log("adj_man_times idx and delta: " + str(idx) + " : " + str(d_time) + " ; " + str(idx), "d")
        idx = (idx % 7) + 1

        ret_tuple = (idx,d_time)
    return ret_tuple
# adj_man_time

def read_keyboard(screen, event_quit, is_man_run, mode, logger, water_dict, last_key):
     
    c = screen.getch()
    if c != curses.ERR:
        if chr(c) == 'q':
            event_quit.set()
            logger.log("Stopped by user - pressed q", "w")
        if chr(c) == 'w':
            mode[0] = "Water"
            water_dict["man_mode"] = 0
            is_man_run[0] = False
            
            logger.log("w pressed: mode = " + str(mode))
        if chr(c) == 't':
            mode[0] = "Temp"
            logger.log("t pressed: mode = " + str(mode))
            
        if chr(c) == 'r':
            is_man_run[0] = True

        idx,delta = adj_man_time(chr(c), logger)
        water_dict['conf']['run_times'][7][idx] += delta
        water_dict['conf']['run_times'][7][idx] = max(0, min(water_dict['conf']['run_times'][7][idx], 99))
        
        #add a bool to the ret tuple for save conf, and write water_dict to file, also d is double used
        day,idx,delta = adj_run_times(chr(c), logger, water_dict)
        water_dict['conf']['run_times'][day][idx] += delta
        water_dict['conf']['run_times'][day][idx] = max(0, min(water_dict['conf']['run_times'][day][idx], 99))
        if chr(c) == 'p' and last_key[0] == 'p':
            #KMDB this call needs to move to ConfFile. 
            last_key[0] = 'a'
            f = open("irrigation.conf", "w")
            f.write(json.dumps(water_dict['conf']))
            f.close()        
        last_key[0] = chr(c)
# read_keyboard

#This needs to be in a thread
def send_update(water_dict, logger):
    request = Request('https://192.168.1.105:7131/', logger)
    
    try:
        n = datetime.now()#("1/4/2024 2:33:09 PM", '%m/%d/%Y %I:%M:%S %p')
        logger.log("n$$$$$$$$$$$$$$$$$$$$: " + str(n))
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%Y %I:%M:%S %p")
        logger.log("current_time [" + str(current_time) + "] formatted_time [" + str(formatted_time) + "]")
        time_delta = current_time - last_successful_update[0]
        if time_delta.seconds > 9:
            try:
                if updateCounter[0] % 3 == 0:
                    newVal[0] = 0
                else:
                    newVal[0] = 1
                logger.log("Sending update [" + str(formatted_time) + "]", 'd')
                last_successful_update[0] = current_time
                data = {
                            #"LastUpdate": str(formatted_time),
                            "IsRainDelay": newVal[0],
                            "RunTimes": water_dict['conf']['run_times']
                            # "RunTimes": [
                            #     [1 + newVal[0], 2, 3, 4, 5, 6, 7, 8],
                            #     [2, 2, 3, 4, 5, 6, 7, 8],
                            #     [3, 2, 3, 4, 5, 6, 7, 8],
                            #     [4, 2, 3, 4, 5, 6, 7, 8],
                            #     [5, 2, 3, 4, 5, 6, 7, 8],
                            #     [6, 2, 3, 4, 5, 6, 7, 8],
                            #     [7, 2, 3, 4, 5, 6, 7, 8],
                            #     [8, 2, 3, 4, 5, 6, 7, 8]
                            # ]
                        }
                        
                updateCounter[0] += 1                      
                #logger.log("calling http_post************************")
                #request.http_post('update', data, {'Content-Type': 'application/json'})
            except Exception as ex:
                logger.log('Exception: ' + str(ex), 'e')
    except Exception as ex:
        logger.log("Exception in SendUpdate: [" + str(ex) + "]", 'e')



app = Flask(__name__)

@app.route('/')
def index():
    #thread.set() stops the thread
    event_stop_water_thread.set()
    return 'WaterThread stopped. Hello, world!'

@app.route('/another-endpoint')
def another_endpoint():
    #read the .conf file and update the water_dict
    
    #try:
        #test_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
        #cf = ConfFile.ConfFile(test_dict['conf'], ll, is_man_run, event_quit)
        #test_dict = cf.read_conf('r')

        #water_dict['conf'] = test_dict
    #except Exception as ex:
    #    ll.log('Exception in /another-endpoint: ' + str(ex), 'e')
    #    event_quit.set()
    
    
    #thread.clear() starts the thread
    event_stop_water_thread.clear()
    return 'WaterThread started. This is another endpoint.'

class ApiThread(threading.Thread):

    def __init__(self, app, e_stop_water_thread):
        threading.Thread.__init__(self)
        count = 0
        self.srv = make_server('0.0.0.0', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()
    
    
    
    
def read_conf_file(ll):
    test_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
    cf = ConfFile.ConfFile(test_dict['conf'], ll, is_man_run, event_quit)
    test_dict = cf.read_conf('r')
    water_dict['conf'] = test_dict

    
    
    
    
    
    
def main(scr):

    scr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    
    scr.keypad(1)
    scr.nodelay(1)

    headder_begin_x = 0; headder_begin_y = 0
    headder_height = 2; headder_width = 80

    body_begin_x = headder_begin_x; body_begin_y = headder_begin_y + headder_height
    body_height = 26; body_width = headder_width

    foot_begin_x = body_begin_x; foot_begin_y = body_begin_y + body_height
    foot_height = 2; foot_width = headder_width

    headder_win = curses.newwin(headder_height, headder_width, headder_begin_y, headder_begin_x)

    body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)
    #temp_body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)

    ll = logger.logger("water", water_dict['conf']['log_level'])    

    # set when operator presses 'q'
    event_quit = threading.Event()

    test_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
    cf = ConfFile.ConfFile(test_dict['conf'], ll, is_man_run, event_quit)
    test_dict = cf.read_conf('r')

    water_dict['conf'] = test_dict

    # We use the logger in ConfFile with the default value 'DEBUG' after loading the conf 
    # file set the log_level to the level in the config file.
    ll.update_log_level(water_dict['conf']['log_level'])   

    # leading 0, 7 valves and manual mode
    run_times_mode = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    rt = ["","","","","","","",""]
    for d in range(7):
        run_times[d] = str(water_dict["conf"]["run_times"][d])
        for t in range(7):
            rt[d] += str(water_dict["conf"]["run_times"][d][t])
        ll.log("setup - run_times[]: " + rt[d])

    server_thread = ApiThread(app, event_stop_water_thread)
    server_thread.start()
    
    # Create new threads
    threads = []
    thread1 = WaterThread.WaterThread(1, "WaterThread", ll, water_dict, event_quit, is_man_run, event_stop_water_thread)
    
    # Start new Threads
    thread1.start()
    #thread2.start()
    #thread3.start()

    # Add threads to thread list
    threads.append(thread1)
    #threads.append(thread2)
    #threads.append(thread3)
    
    #run_flask()
    
    request = Request('https://192.168.1.105:7131/', ll)
    
    try:
        n = datetime.now()#("1/4/2024 2:33:09 PM", '%m/%d/%Y %I:%M:%S %p')
        ll.log("n$$$$$$$$$$$$$$$$$$$$: " + str(n))
        
        current_time = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        #formatted_time = current_time.strftime("%m/%d/%Y %I:%M:%S %p")
        ll.log("formatted_time:$$$$$$$$$$$ " + str(current_time))
        
        
        data = {
                    "LastUpdate": str(current_time),
                    "IsRainDelay": 0,
                    "RunTimes": [
                        [1],
                        [2]
                    ]
                }
        ll.log("calling http_post************************")
        #request.http_post('update', data, {'Content-Type': 'application/json'})
    except Exception as ex:
        ll.log('Exception: ' + str(ex), 'e')
    #event_quit.set()

    
    
    #mail = e_mail.e_mail()
    #now = datetime.now()
    
    #mail.send_mail('from WaterThread ctor', str(now))
    count = 0
    while not event_quit.is_set():

        # Move cf = ConfFile.ConfFile(test_dict['conf'], ll, is_man_run, event_quit)
        # and all the other loading into a function that is called here when an event is set/cleared.
        # The flask endpoints will set the event and the main loop will call the function to reload the conf file.

        send_update(water_dict, ll)
        read_keyboard(scr, event_quit, is_man_run, mode, ll, water_dict, last_key)

        ll.log("main is_man_run[0]: " + str(is_man_run[0]))

        ll.log("Water THREAD is_alive(): " + str(threads[0].is_alive()))

        ll.log("water_dict['man_mode']: " + str(water_dict["man_mode"]), "d")
        if water_dict["man_mode"] == 0:
            mode[0] = "Water"
        ll.log("water_dict['man_mode']: " + str(water_dict["man_mode"]), "d")
        ll.log("is_man_run[0]: " + str(is_man_run[0]))
        ll.log("water_dict['conf']: " + str(water_dict['conf']), "d")

        display_head(headder_win, ll, mode[0])
        display_foot(foot_win, ll)
        display_body(body_win, ll)
        
        headder_win.refresh()
        body_win.refresh()
        foot_win.refresh()

        if threads[0].is_alive() and event_stop_water_thread.is_set():
            ll.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$threads[0].is_alive() and event_stop_water_thread.is_set() is True", "d")
            #threads[0].shutdown()
            threads[0].join()
            #cf.write_conf(water_dict['conf'])
            #thread1 = WaterThread.WaterThread(1, "WaterThread", ll, water_dict
        elif not threads[0].is_alive() and not event_stop_water_thread.is_set():
            ll.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@not threads[0].is_alive() and not event_stop_water_thread.is_set() is True", "d")
            
            test_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
            cf = ConfFile.ConfFile(test_dict['conf'], ll, is_man_run, event_quit)
            test_dict = cf.read_conf('r')
            water_dict['conf'] = test_dict
            #read_conf_file(ll)
            
            thread1 = WaterThread.WaterThread(1, "WaterThread", ll, water_dict, event_quit, is_man_run, event_stop_water_thread)
            thread1.start()
            threads[0] = thread1
        time.sleep(1.1)

    # Wait for all threads to complete
    server_thread.shutdown()
    server_thread.join()
    for t in threads:
        ll.log("JOIN")
        t.join()

    scr.refresh()
    scr.clear()
# def main

if __name__ == '__main__':
    try:
        exit_string = "Quit by user or to reload conf file"
        curses.wrapper(main)
    except Exception as ex:
        print("Exception in main() loop, trying to continue: " + str(ex))
        exit_string = "Quit on error"
    finally:
        curses.endwin()
        print(exit_string)
# if __name__
