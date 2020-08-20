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
        #self.alpha = cfgObj.alpha
        #except Exception, ex:
        #    sys.exit("Error in " + "DaqcPlate")

    def get_adc(self, idx):
        v = DAQC.getADC(0, idx)
        #print("idx: " + str(idx) + " v: " + str(v))
        return v# DAQC.getADC(self.pid, idx)
    #get_adc

    def get_temp(self, idx, scale):
        v = DAQC.getTEMP(0, idx, scale)
        print("idx: " + str(idx) + " v: " + str(v))
        return v # DAQC.getTEMP(0, idx, scale)
    
    def km(self):
        return 5

    #def get_temp(self, idx):
    #    temp = 100 * self.get_adc(idx) - 50
    #    temp = self.lp_filter(temp)
    #    return temp
    #get_temp

    #def read_adc(self):
    #    tm = time.time()
    #    t1 = self.get_temp(0)
    #    t2 = self.get_temp(1)
    #    t3 = self.get_temp(2)
    #    v  = self.get_adc(3)
    #    return {'time': tm, 't1': t1, 't2': t2, 't3': t3, 'v': v }
    #read_adc

    #def lp_filter(self, raw):
    #    filt = (1 - self.alpha) * raw + self.alpha * raw
    #    filt = round(filt, 1)
    #    return filt
#DacqPlate
