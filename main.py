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

    e = threading.Event()
    threads = []
    ll = logger.logger("main")

    # Create new threads
    thread1 = sprinklerThread.sprinklerThread(1, "sprinklerThread", sprinkler_dict, e)
    thread2 = tempThread.daqcThread(2, "daqcThread", daqc_dict, e)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)
   
    c = 20
    while c < 20:
        adb = ADBoard(0, e)
        v = adb.get_adc(0)
        #print("After threads.append" + str(v))
        v = adb.get_adc(1)
        #print("After threads.append" + str(v))
        v = adb.get_adc(2)
        #print("After threads.append" + str(v))
        v = adb.get_adc(3)
        #print("After threads.append" + str(v))
        v = adb.get_adc(4)
        #print("After threads.append" + str(v))
        v = adb.get_adc(5)
        #print("After threads.append" + str(v))
        v = adb.get_adc(6)
        #print("After threads.append" + str(v))
        v = adb.get_adc(7)
        #print("After threads.append" + str(v))
        time.sleep(1)
        c += 1

    ct = 0
    while ct < 1000:
        ll.log("main: " + str(ct))
        #scr.addstr(5,5,"Woot: " + str(ct))
        time.sleep(5)
        scr.addstr(6,5,  "sprinkler: " + str(sprinkler_dict[0]))
        scr.addstr(7,5,  "daqc: " + str(daqc_dict[0]))
        scr.addstr(8,5,  "daqc: " + str(daqc_dict[1]))
        scr.addstr(9,5,  "daqc: " + str(daqc_dict[2]))
        ll.log("t0: " + str(daqc_dict[0]))
        ll.log("t1: " + str(daqc_dict[1]))
        ll.log("t2: " + str(daqc_dict[2]))

        scr.refresh()
        ct += 1

    e.set()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    scr.refresh()

    #curses.endwin()

# def main

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    finally:
        curses.endwin()
# if __name__


