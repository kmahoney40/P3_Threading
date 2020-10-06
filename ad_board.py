from daqc_plate import DaqcPlate
import sys
import time
import logger

class ADBoard(DaqcPlate):
    def __init__(self, pid, logger, cfgObj):
        #try:
        self.name = "ADBoard_" + str(pid)
        self.pid = pid
        self.last_temp = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
        self.limit_counter = [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]]
        #self.ll = logger.logger("ADBoard __int__ called")
        self.ll = logger
        self.alpha = 0.075 #cfgObj.alpha
    # __INIT__    

    def get_adc(cls, idx):
        return DaqcPlate.get_adc(cls.pid, idx)
    #get_adc

    def get_temp(cls, idx, scale='f'):
        return DaqcPlate.get_temp(cls.pid, idx, scale)
    # get_temp

    def get_adc_temp(cls, idx, scale='f'):
        adc = cls.get_adc_filter(idx)
        temp = adc * 100.0 - 50.0
        cls.ll.log("scale: " + scale)
        if(scale.lower() == 'f'):
            temp = temp * (9.0/5.0) + 32
        return temp
    # get_adc_temp

    def get_adc_filter(cls, idx):
        raw = cls.get_adc(idx)
        cls.ll.log("get_adc_filter idx: " + str(idx) + " raw: " + str(raw))
        if not cls.limit_d(raw, idx):
            cls.last_temp[idx] = cls.filter(raw, cls.last_temp[idx]) 
        cls.ll.log("last_temp[idx]: " + str(cls.last_temp[idx]))
        c = 100.0 * cls.last_temp[idx] - 50.0
        f = c * (9.0/5.0) + 32.0
        cls.ll.log("TEMP IN C id " + str(idx) + " " + str(c))
        cls.ll.log("TEMP IN F id " + str(idx) + " " + str(f))
        return cls.last_temp[idx]
    # get_adc_filter

    def filter(cls, raw, last):
        new = cls.alpha * (raw - last) + last
        return new
    # filter

    def limit_d(cls, raw, idx):
        ret_val = False
        # 0.4 is 22 def F, assume it is an error
        if abs(raw - cls.last_temp[idx] ) > .03:
            cls.limit_counter[1][idx] += 1
        else:
            cls.limit_counter[1][idx] += 0
        if raw > 0.4:
            cls.limit_counter[0][idx] = 0
            ret_val = False
        else:
            cls.limit_counter[0][idx] += 1
            ret_val = True
        cls.ll.log("#############                raw " + str(raw))
        cls.ll.log("############# limit_counter[0][" + str(idx) + "] " + str(cls.limit_counter[0][idx]))
        cls.ll.log("############# limit_counter[1][" + str(idx) + "] " + str(cls.limit_counter[1][idx]))
        return ret_val
    # limit_d

#DacqPlate
