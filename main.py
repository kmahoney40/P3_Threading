import threading
import time
import curses

# These will become JSON
sprinkler_dict = [1,2,3]
daqc_dict = [0] 

# This calss will read/write all the commands to run the sprinklers. At this point a single
# relay-plate. The shared innput dictioary can be expanded to include weahter data that may be used
# to dynamically modife runtimes.
class sprinklerThread(threading.Thread):
    def __init__(self, threadID, name, counter, in_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict

    def run(self):
        #print("Starting " + self.name)
        while 1:
            self.in_dict[0] += 1
            time.sleep(1)

# The daqcThread calss will read/write the daqc-plate and a relay-plate to monitor temps in and
# outside of the garage and control an exhaust fan.
class daqcThread(threading.Thread):
    def __init__(self, threadID, name, counter, in_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.in_dict = in_dict

    def run(self):
        #print("Starting " + self.name)
        while 1:            
            self.in_dict[0] += 1
            time.sleep(5)


def main(scr):

    scr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    scr.keypad(1)
    scr.nodelay(1)

    threads = []

    # Create new threads
    thread1 = sprinklerThread(1, "sprinklerThread", 0, sprinkler_dict)
    thread2 = daqcThread(2, "daqcThread", 0, daqc_dict)
    #thread3 = uiThread(3, "uiThread", 0, sprinkler_dict, daqc_dict, scr)

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

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print ("Exiting Main Thread")

    scr.refresh()

    curses.endwin()

if __name__ == '__main__':
       
    curses.wrapper(main)
        
