from datetime import datetime
import time
import sys


def display_head(win, logger, mode, water_dict):
    try:
        now = datetime.now()
        now_formated = now.strftime("%m/%d/%Y, %H:%M:%S")#datetime.now()
        win.addstr(0, 0, "Now: " +  now_formated + "   Mode: " + mode + " Auto Start Time: " + str(water_dict["conf"]["start_time"]))
        win.clrtoeol()
    except:
        logger.log("Error in display_head: " + str(sys.exc_info()[0]))
# display_head

def display_body(win, logger, water_dict):
    try:
        win.addstr(0, 0, "Start Time: " + str(water_dict["conf"]["start_time"]))
        num_runs = len(water_dict["conf"]["run_times"])
        num_valves = 7
        days = ["Mon ", "Tue ", "Wed ", "Th  ", "Fri ", "Sat ", "Sun "]

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
        
        logger.log("water_dict['conf']['run_times'][7]: " + str(water_dict['conf']['run_times'][7]))
    except:
        logger.log("Error in display_body: " + str(sys.exc_info()[0]))
# display_body

def display_foot(win, logger, underline):
    try:
        win.addstr(0, 0, "Footer line 1", underline)
        win.addstr(1, 0, "FooterLine 2", underline)
    except:
        logger.log("Error in display_foot: " + str(sys.exc_info()[0]))
# display_foot
