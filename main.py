import threading
from datetime import datetime
import time
import curses
import sys
import json
import WaterThread
import TempThread
import logger
import e_mail

# These will become JSON
#water_dict = [0, {"start_time": 600}]
water_dict = { "valve_status": 0, "man_mode": 0, "man_run": 0, "time_remaining": " ", "conf": {} }
daqc_dict = [0,0,0,0,0,0,0,0]
days = ["Mon ", "Tue ", "Wed ", "Th  ", "Fri ", "Sat ", "Sun "]
mode = ["Water"]
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
        logger.log("@@@@@@@@@@@@@@ display2_body: " + str(sys.exc_info()[0]), "d")
    except:
        logger.log("Error in display2_body: " + str(sys.exc_info()[0]), "e")

def display_foot(win, logger):
    try:
        win.addstr(0, 0, str(7), curses.A_UNDERLINE)
        win.addstr(1, 1, str(8), curses.A_UNDERLINE)
    except:
        logger.log("Error in display_foot: " + str(sys.exc_info()[0]))
# display_foot

def adj_man_time(inCh, logger):
    
    dt = 1
    idx = 0
    man = False
    retVal = (0,0,man)

    logger.log("OUTSIDE adj_man_times inCh: " + str(inCh), "d")

    lst = ['a','s','d','f','g','h','j','A','S','D','F','G','H','J','z','x','c','v','b','n','m','Z','X','C','V','B','N','M']
    if inCh in lst:
        logger.log("INSIDE adj_man_times inCh: " + str(inCh), "d")
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

def read_keyboard(screen, event_quit, event_man_run, mode, logger):
    ret_val = True
    escapekey = False
    c = screen.getch()
    if escapekey:
        c = 27
        escapekey = False
    if c != curses.ERR:
        if chr(c) == 'q':
            event_quit.set()
            logger.log("Stopped by user - pressed q", "w")
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
            #logger.log("man_mode = " + str(water_dict["man_mode"]))
            if chr(c) == 'r' and water_dict["man_mode"] is 1:
                water_dict["man_run"] = 1
                event_man_run.set()

            idx,delta,man_run = adj_man_time(chr(c), logger)
            #logger.log("idx,delta = " + str(idx) + "," + str(delta) + "," + str(man_run), "d")
            water_dict['conf']['man_times'][idx] += delta
            # This is better that the comment block below to keep man_times between 0 and 99 (inclusive)
            water_dict['conf']['man_times'][idx] = max(0, min(water_dict['conf']['man_times'][idx], 99))
            # Save this block            
            #if water_dict['conf']['man_times'][idx] > 99:
            #    water_dict['conf']['man_times'][idx] = 99
            #if water_dict['conf']['man_times'][idx] < 0:
            #    water_dict['conf']['man_times'][idx] = 0
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

    body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)
    temp_body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)

    escapekey = False
    send_mail = True
    mail = e_mail.e_mail()


    # Read conf file
    conf_file = open("irrigation.conf", "r")
    conf_data = conf_file.read()
    conf_json = json.loads(conf_data)
    water_dict['conf'] = conf_json

    ll = logger.logger("water", water_dict['conf']['log_level'])    


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


    # todo Use Dictionary quit:, t1: or water_event, t2 or temp_event
    event_quit = threading.Event()
    event_man_run = threading.Event()
    #water_events = [event_quit, event_man_run]
    #temp_events = [event_quit, event_temp_update]
    # Create new threads
    threads = []
    thread1 = WaterThread.WaterThread(1, "WaterThread", ll, water_dict, event_quit, event_man_run)
    thread2 = TempThread.daqcThread(2, "daqcThread", ll, daqc_dict, event_quit)
    
    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)
   
   
    #id = 0
    keep_going = True
    while keep_going:
        # Returns False if 'q' is pressed
        if not read_keyboard(scr, event_quit, event_man_run, mode, ll):
            break
        display_head(headder_win, ll, mode[0])
        if mode[0] == "Water":
            display_body(body_win, ll)
        else:
            display2_body(temp_body_win, ll)
        display_foot(foot_win, ll)

        #id += 1
        headder_win.refresh()
        body_win.refresh()
        foot_win.refresh()
        
        
        now = datetime.now()
        if(now.minute >= 0 and send_mail):
            mail.send_mail(None, str(now))
            send_mail = False
        
        time.sleep(1.1)

    # Wait for all threads to complete
    for t in threads:
        ll.log("JOIN")
        t.join()

    scr.refresh()
# def main

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    finally:
        curses.endwin()
# if __name__


