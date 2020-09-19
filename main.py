import threading
from datetime import datetime
import time
import curses
import sys
import json
import WaterThread
import tempThread
import logger

# These will become JSON
#water_dict = [0, {"start_time": 600}]
water_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "conf": {} }
daqc_dict = [0,0,0,0,0,0,0,0]
days = ["Mon ", "Tue ", "Wed ", "Th  ", "Fri ", "Sat ", "Sun "]
mode = ["Water"]
#man_run = False

def display_head(win, logger, mode):
    try:
        now = datetime.now()
        now_formated = now.strftime("%m/%d/%Y, %H:%M:%S")#datetime.now()
        win.addstr(0, 0, "Now: " +  now_formated + "   Mode: " + mode)
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
                on_off = "ON"
            win.addstr(0 + valve, 0, "Valve " + str(valve) + " state: " + on_off)
            win.clrtoeol()

        for run in range(num_runs):
            win.addstr(0 + run, 43, days[run] + str(water_dict["conf"]["run_times"][run]))
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

def display_foot(win, logger):
    try:
        win.addstr(0, 0, str(7), curses.A_UNDERLINE)
        win.addstr(1, 1, str(8), curses.A_UNDERLINE)
    except:
        logger.log("Error in display_body: " + str(sys.exc_info()[0]))
# display_foot

def adj_man_time(inCh, logger):
    
    dt = 1
    idx = 0
    man = False
    retVal = (0,0,man)

    lst = ['a','s','d','f','g','h','j','A','S','D','F','G','H','J','z','x','c','v','b','n','m','Z','X','C','V','B','N','M']
    if inCh == 'r':
        man = True
        water_dict["man_run"] = 1
    elif inCh in lst:
        # idx is for a list and we want to skip the 1st element
        idx = lst.index(inCh)
        if inCh.isupper():
            dt = 5
        if idx > 13:
            dt *= -1
        logger.log("adj_man_times idx and delta: " + str(idx) + " : " + str(dt) + " ; " + str(idx), "d")
        idx = (idx % 7) + 1
    retVal = (idx,dt,man)
    return retVal
# adj_man_time

def read_keyboard(screen, event_quit, mode, logger):
    ret_val = True
    escapekey = False
    c = screen.getch()
    if escapekey:
        c = 27
        escapekey = False
    if c != curses.ERR:
        if chr(c) == 'q':
            event_quit.set()
            ret_val = False
        if chr(c) == 'w':
            mode[0] = "Water"
            water_dict["man_mode"] = 0
            #water_dict["man_run"] = 0
            logger.log("w pressed: mode = " + str(mode))
        if chr(c) == 't':
            mode[0] = "Temp"
            logger.log("t pressed: mode = " + str(mode))
        if chr(c) == 'm':
            if mode[0] == "Water":
                mode[0] = "Water/Manual"
                water_dict["man_mode"] = 1
                logger.log("m pressed: mode = " + str(mode))
        if c is 27:
            if mode[0] == "Water/Manual":
                mode[0] = "Water"
                logger.log("m pressed: mode = " + str(mode))
            
        if mode[0] == "Water/Manual":
            idx,delta,man_run = adj_man_time(chr(c), logger)
            logger.log("idx,delta = " + str(idx) + "," + str(delta) + "," + str(man_run), "d")
            water_dict['conf']['man_times'][idx] += delta
            if water_dict['conf']['man_times'][idx] > 99:
                water_dict['conf']['man_times'][idx] = 99
            if water_dict['conf']['man_times'][idx] < 0:
                water_dict['conf']['man_times'][idx] = 0
                
    return ret_val
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
    body_height = 27; body_width = headder_width

    foot_begin_x = body_begin_x; foot_begin_y = body_begin_y + body_height
    foot_height = 2; foot_width = headder_width

    headder_win = curses.newwin(headder_height, headder_width, headder_begin_y, headder_begin_x)
    #headder_win.border()
    
    body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)
    #body_win.border()

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)
    #foot_win.border()

    escapekey = False
    ll = logger.logger("main")


    # Read conf file
    conf_file = open("irrigation.conf", "r")
    conf_data = conf_file.read()
    conf_json = json.loads(conf_data)
    water_dict['conf'] = conf_json
    ll.log("setup - water_dict['valve_status']: " + str(water_dict['valve_status']))
    ll.log("setup - water_dict['conf']: " + str(water_dict['conf']))
    ll.log("setup - water_dict['conf']['start_time']: " + str(water_dict['conf']['start_time']))
    ll.log("setup - water_dict['conf']['pid']: " + str(water_dict['conf']['pid']))


    # todo Use Dictionary quit:, t1: or water_event, t2 or temp_event
    event_quit = threading.Event()
    update_events = [threading.Event(), threading.Event()]
    # Create new threads
    threads = []
    thread1 = WaterThread.WaterThread(1, "WaterThread", water_dict, event_quit, update_events[0])
    thread2 = tempThread.daqcThread(2, "daqcThread", daqc_dict, event_quit, update_events[1])
    
    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)
   
   
    id = 0
    keep_going = True
    while keep_going:
        # Returns False if 'q' is pressed
        if not read_keyboard(scr, event_quit, mode, ll):
            break
        #ll.log("mode = " + mode[0])
#        c = scr.getch()
#        if escapekey:
#            c = 27
#            escapekey = False
#        if c != curses.ERR:
#            if chr(c) == 'q':
#                keep_going = False
#                e.set()
#                break

        if update_events[0].is_set():
            ll.log("WaterThread update event")
            ll.log("WaterThread status/state: " + str(water_dict["valve_status"]))
            update_events[0].clear()
        if update_events[1].is_set(): 
            ll.log("thread update event")
            update_events[1].clear()

        display_head(headder_win, ll, mode[0])
        display_body(body_win, ll)
        display_foot(foot_win, ll)

        id += 1
        headder_win.refresh()
        body_win.refresh()
        foot_win.refresh()
        #scr.refresh()
        time.sleep(0.1)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    scr.refresh()
# def main

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    finally:
        curses.endwin()
# if __name__


