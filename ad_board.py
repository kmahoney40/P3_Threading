from daqc_plate import DaqcPlate
import sys
import time
import logger

class ADBoard(DaqcPlate):
    def __init__(self, pid, cfgObj):
        #try:
        self.name = "ADBoard_" + str(pid)
        self.pid = pid
        self.last_temp = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
        self.ll = logger.logger("ADBoard __int__ called")
        self.alpha = 0.1 #cfgObj.alpha
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
        cls.last_temp[idx] = cls.filter(raw, cls.last_temp[idx]) 
        cls.ll.log("last_temp[idx]: " + str(cls.last_temp[idx]))
        return cls.last_temp[idx]
    # get_adc_filter

    def filter(cls, raw, last):
        new = cls.alpha * (raw - last) + last
        return new

#DacqPlate
