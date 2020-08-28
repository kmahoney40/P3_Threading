import threading
import time
import curses
import sprinklerThread
import tempThread
import logger
from ad_board import ADBoard

# These will become JSON
sprinkler_dict = [1,2,3]
daqc_dict = [0,0,0,0,0,0,0,0] 

def main(scr):

    scr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    scr.keypad(1)
    scr.nodelay(1)

    headder_begin_x = 0; headder_begin_y = 0
    headder_height = 5; headder_width = 80

    body_begin_x = headder_begin_x; body_begin_y = headder_begin_y + headder_height
    body_height = 20; body_width = headder_width

    foot_begin_x = body_begin_x; foot_begin_y = body_begin_y + body_height
    foot_height = 5; foot_width = headder_width

    headder_win = curses.newwin(headder_height, headder_width, headder_begin_y, headder_begin_x)
    headder_win.border()
    
    body_win = curses.newwin(body_height, body_width, body_begin_y, body_begin_x)
    body_win.border()

    foot_win = curses.newwin(foot_height, foot_width, foot_begin_y, foot_begin_x)
    foot_win.border()

    e = threading.Event()
    update_events = [threading.Event(), threading.Event()]
    escapekey = False
    threads = []
    ll = logger.logger("main")

    # Create new threads
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
        c = scr.getch()
        if escapekey:
            c = 27
            escapekey = False
        if c != curses.ERR:
            if chr(c) == 'q':
                keep_going = False
                e.set()
                break
        if update_events[0].is_set():
            ll.log("sprinklerThread update event")
            update_events[0].clear()
        if update_events[1].is_set(): 
            ll.log("thread update event")
            update_events[1].clear()
        headder_win.addstr(0, 0, str(id), curses.A_UNDERLINE)
        headder_win.addstr(1, 1, str(id), curses.A_UNDERLINE)
        headder_win.addstr(2, 2, str(id), curses.A_BOLD)
        headder_win.addstr(3, 3, str(id), curses.A_DIM)
        headder_win.addstr(4, 4, str(id), curses.A_STANDOUT)

        body_win.addstr(0, 0, str(id), curses.A_UNDERLINE)
        body_win.addstr(19, 0, str(id), curses.A_UNDERLINE)


        foot_win.addstr(0, 0, str(id), curses.A_UNDERLINE)
        foot_win.addstr(1, 1, str(id), curses.A_UNDERLINE)
        foot_win.addstr(2, 2, str(id), curses.A_BOLD)
        foot_win.addstr(3, 3, str(id), curses.A_DIM)
        foot_win.addstr(4, 4, str(id), curses.A_STANDOUT)
        id += 1
        headder_win.refresh()
        body_win.refresh()
        foot_win.refresh()
        scr.refresh()
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


