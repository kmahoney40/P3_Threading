import threading
from datetime import datetime
import time
import curses
import sys
import json
import sprinklerThread
import tempThread
import logger

# These will become JSON
#sprinkler_dict = [0, {"start_time": 600}]
sprinkler_dict = { "valve_status": 0, "conf": {} }
daqc_dict = [0,0,0,0,0,0,0,0] 
mode = ["Water"]

def display_head(win, logger, mode):
    try:
        now = datetime.now()
        now_formated = now.strftime("%m/%d/%Y, %H:%M:%S")#datetime.now()
        win.addstr(0, 0, "Now: " +  now_formated + "   Mode: " + mode)
        win.addstr(1, 0, str(2), curses.A_UNDERLINE)
    except:
        logger.log("Error in display_head: " + str(sys.exc_info()[0]))
# display_head

def display_body(win, logger):
    try:
        win.addstr(0, 0, "Start Time: " + str(sprinkler_dict["conf"]["start_time"]))
        #win.addstr(1,5,str(sprinkler_dict[0]))
        win.addstr(26, 0, str(6), curses.A_UNDERLINE)
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
            logger.log("w pressed: mode = " + str(mode))
        if chr(c) == 't':
            mode[0] = "Temp"
            logger.log("t pressed: mode = " + str(mode))
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
    headder_win.border()
    
    body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)
    body_win.border()

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)
    foot_win.border()

    escapekey = False
    ll = logger.logger("main")


    # Read conf file
    conf_file = open("irrigation.conf", "r")
    conf_data = conf_file.read()
    conf_json = json.loads(conf_data)
    sprinkler_dict['conf'] = conf_json
    ll.log("setup - sprinkler_dict['valve_status']: " + str(sprinkler_dict['valve_status']))
    ll.log("setup - sprinkler_dict['conf']: " + str(sprinkler_dict['conf']))
    ll.log("setup - sprinkler_dict['conf']['start_time']: " + str(sprinkler_dict['conf']['start_time']))
    ll.log("setup - sprinkler_dict['conf']['pid']: " + str(sprinkler_dict['conf']['pid']))


    # todo Use Dictionary quit:, t1: or sprinkler_eveint, t2 or temp_event
    e = threading.Event()
    update_events = [threading.Event(), threading.Event()]
    # Create new threads
    threads = []
    thread1 = sprinklerThread.sprinklerThread(1, "sprinklerThread", sprinkler_dict, e, update_events[0])
    thread2 = tempThread.daqcThread(2, "daqcThread", daqc_dict, e, update_events[1])
    
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
        if not read_keyboard(scr, e, mode, ll):
            break
        ll.log("mode = " + mode[0])
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
            ll.log("sprinklerThread update event")
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


