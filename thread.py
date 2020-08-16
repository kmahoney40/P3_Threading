import threading
import time

sprinkler_dict = [1,2,3]
daqc_dict = [0] 

class sprinklerThread(threading.Thread):
    def __init__(self, threadID, name, counter, in_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.in_dict = in_dict

    def run(self):
        print("Starting " + self.name)
        while 1:
            #threadLock.acquire()
            print_time(self.name, self.counter, 1)
            #threadLock.release()
            self.in_dict[0] += 1
            time.sleep(1)

def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

class daqcThread(threading.Thread):
    def __init__(self, threadID, name, counter, in_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.in_dict = in_dict

    def run(self):
        print("Starting " + self.name)
        while 1:            
            #threadLock.acquire()
            print_time(self.name, self.counter, 1)
            #threadLock.release()
            self.in_dict[0] += 1
            time.sleep(5)

class uiThread(threading.Thread):
    def __init__(self, threadID, name, counter, in_dict, daqc_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.in_dict = in_dict
        self.daqc_dict = daqc_dict

    def run(self):
        print("Starting " + self.name)
        while 1:
            print_time(self.name, self.counter, 1)
            print("in_dict " + str(self.in_dict[0]))
            print("daqc_dict " + str(self.daqc_dict[0]))
            time.sleep(1)

threadLock = threading.Lock()
threads = []

# Create new threads
thread1 = sprinklerThread(1, "sprinklerThread", 0, sprinkler_dict)
thread2 = daqcThread(2, "daqcThread", 0, daqc_dict)
thread3 = uiThread(3, "uiThread", 0, sprinkler_dict, daqc_dict)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)

# Wait for all threads to complete
for t in threads:
    t.join()
print ("Exiting Main Thread")

