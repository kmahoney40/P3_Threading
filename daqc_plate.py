import piplates.DAQCplate as DAQC
import sys
import time
import logger

class DaqcPlate:
    def __init__(self, pid, cfgObj):
        #try:
        self.name = "DaqcPlate_" + str(pid)
        self.pid = pid
        self.ll = logger.logger("DaqcPlate __int__ called")

    def get_adc(cls, idx):
        v = DAQC.getADC(0, idx)
        return v# DAQC.getADC(cls.pid, idx)
    #get_adc

    def get_temp(cls, idx, scale):
        v = DAQC.getTEMP(0, idx, scale)
        print("idx: " + str(idx) + " v: " + str(v))
        return v # DAQC.getTEMP(0, idx, scale)
    
#DaqcPlate
