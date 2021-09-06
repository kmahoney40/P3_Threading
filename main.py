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
import e_mail



# These will become JSON
#water_dict = [0, {"start_time": 600}]
water_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", 
                "conf": {
                    "start_time": 600,
                    "pid": 0,
                    "alpha": 0.075,
                    "log_level": "DEBUG",
                    "man_times": [0, 0, 0, 0, 0, 0, 0, 0],
                    "run_times": [
                        [0, 10, 15,  0,  0, 15, 15, 10],
                        [10, 10,  10,  0, 45,  10, 10, 10],
                        [0, 10, 15,  0,  0, 15, 15, 10],
                        [10,  0,  0,  0,  0,  0,  0,  0],
                        [5, 5,  0,  0,  0, 15, 0,  5],
                        [0,  0, 15,  0, 45,  0,  0,  0],
                        [0, 10,  0,  5,  0,  5,  5,  0]
                    ]
                }
            }

daqc_dict = [0,0,0,0,0,0,0,0]
days = ["Mon ", "Tue ", "Wed ", "Th  ", "Fri ", "Sat ", "Sun "]
mode = ["Water"]
e_mode = ""
#man_run = False
run_times = ["", "", "", "", "", "", ""]
disp_run_times = []

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

        for run in range(num_runs):
            # Packing a lot into one line, love slice.
            win.addstr(0 + run, 43, days[run] + str((water_dict["conf"]["run_times"][run])[1:]))
            win.clrtoeol()
            
        if mode[0] == "Water/Manual":
            win.addstr(8, 0, "Up: 'a' 's' 'd' 'f' 'g' 'h' 'j'")
            # man_times length is 8, extra is used in calculations in WaterThread
            for v in range(1,len(water_dict['conf']['man_times'])):
                win.addstr(9, 3 + (v-1)*4, str(water_dict['conf']['man_times'][v]).rjust(3)) 
            win.addstr(10, 0, "Dn: 'z' 'x' 'c' 'v' 'b' 'n' 'm'")
        else:
            win.move(8,0)
            win.clrtoeol()
            win.move(9,0)
            win.clrtoeol()
            win.move(10,0)
            win.clrtoeol()
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

def adj_man_time(inCh, logger):
    
    d_time = 1
    idx = 0
    ret_tuple = (0,0)

    logger.log("OUTSIDE adj_man_times inCh: " + str(inCh), "d")

    valid_key_press = ['a','s','d','f','g','h','j','A','S','D','F','G','H','J','z','x','c','v','b','n','m','Z','X','C','V','B','N','M']
    if inCh in valid_key_press:
        logger.log("INSIDE adj_man_times inCh: " + str(inCh), "d")
        # idx is for a list and we want to skip the 1st element, as the frist element of run_times is not actually a ru time
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

def read_keyboard(screen, event_quit, event_man_run, mode, logger):
     
    c = screen.getch()
    if c != curses.ERR:
        if chr(c) == 'q':
            event_quit.set()
            logger.log("Stopped by user - pressed q", "w")
        if chr(c) == 'w':
            mode[0] = "Water"
            water_dict["man_mode"] = 0
            event_man_run.clear()
            
            logger.log("w pressed: mode = " + str(mode))
        if chr(c) == 't':
            mode[0] = "Temp"
            logger.log("t pressed: mode = " + str(mode))
        if chr(c) == 'm':
            if mode[0] == "Water":
                mode[0] = "Water/Manual"
                water_dict["man_mode"] = 1
                logger.log("m pressed: mode = " + str(mode))
            
        if mode[0] == "Water/Manual":
            if chr(c) == 'r':
                event_man_run.set()

            idx,delta = adj_man_time(chr(c), logger)
            water_dict['conf']['man_times'][idx] += delta
            water_dict['conf']['man_times'][idx] = max(0, min(water_dict['conf']['man_times'][idx], 99))
# read_keyboard

    
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
    temp_body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)

    ll = logger.logger("water", water_dict['conf']['log_level'])    

    # set when operator presses 'q'
    event_quit = threading.Event()
    event_reload = threading.Event()
    event_man_run = threading.Event()

    test_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
    cf = ConfFile.ConfFile(test_dict['conf'], ll, event_quit)
    test_dict = cf.read_conf('r')

    water_dict['conf'] = test_dict

    # We use the logger in ConfFile with the defualt value 'DEBUG' after loading the conf 
    # file set the log_level to the level in the config file.
    ll.update_log_level(water_dict['conf']['log_level'])   


    ll.log("setup - water_dict['valve_status']: " + str(water_dict['valve_status']))
    ll.log("setup - water_dict['conf']: " + str(water_dict['conf']))
    ll.log("setup - water_dict['conf']['start_time']: " + str(water_dict['conf']['start_time']))
    ll.log("setup - water_dict['conf']['pid']: " + str(water_dict['conf']['pid']))

    rt = ["","","","","","","",""]
    for d in range(7):
        run_times[d] = str(water_dict["conf"]["run_times"][d])
        for t in range(7):
            rt[d] += str(water_dict["conf"]["run_times"][d][t])
        ll.log("setup - run_times[]: " + rt[d])

    # Create new threads
    threads = []
    thread1 = WaterThread.WaterThread(1, "WaterThread", ll, water_dict, event_quit, event_man_run)
    thread2 = TempThread.daqcThread(2, "daqcThread", ll, daqc_dict, event_quit)
    #thread3 = HttpThread.HttpThread(3, "httpThread", ll, water_dict, event_quit)
    
    # Start new Threads
    thread1.start()
    thread2.start()
    #thread3.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)
    #threads.append(thread3)
   
    mail = e_mail.e_mail()
    now = datetime.now()
    mail.send_mail('from WaterThread ctor', str(now))
   
    while not event_quit.is_set():
        
        read_keyboard(scr, event_quit, event_man_run, mode, ll)

        if cf.check_for_update(water_dict['conf']):
            #event_quit.set()
            test_dict = cf.read_conf('r')
            water_dict['conf'] = test_dict

            #temp = cf.read_conf('r')
            #ll.log("read_conf(): " + str(temp))
            #water_dict['conf'] = cf.read_conf('r')

        ll.log("water_dict['man_mode']: " + str(water_dict["man_mode"]) + " $$$$$$", "i")
        if water_dict["man_mode"] is 0:
            mode[0] = "Water"
        ll.log("water_dict['man_mode']: " + str(water_dict["man_mode"]) + " #####")
        ll.log("water_dict['conf']: " + str(water_dict['conf']))

        display_head(headder_win, ll, mode[0])
        #if mode[0] == "Water":
        #    display_body(body_win, ll)
        #else:
        #    display2_body(temp_body_win, ll)
        display_foot(foot_win, ll)
        display_body(body_win, ll)
        
        headder_win.refresh()
        body_win.refresh()
        foot_win.refresh()

        time.sleep(1.1)

    # Wait for all threads to complete
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
