import threading
import time
import curses
import sprinklerThread
import tempThread

# These will become JSON
sprinkler_dict = [1,2,3]
daqc_dict = [0] 

def main(scr):

    scr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    scr.keypad(1)
    scr.nodelay(1)

    e = threading.Event()
    threads = []

    # Create new threads
    thread1 = sprinklerThread.sprinklerThread(1, "sprinklerThread", sprinkler_dict, e)
    thread2 = tempThread.daqcThread(2, "daqcThread", daqc_dict, e)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)
    
    print("After threads.append")

    ct = 0
    while ct < 10:
        scr.addstr(5,5,"Woot: " + str(ct))
        time.sleep(1)
        scr.addstr(6,5, "sprinkler: " + str(sprinkler_dict[0]))
        scr.addstr(7,5, "daqc: " + str(daqc_dict[0]))
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


