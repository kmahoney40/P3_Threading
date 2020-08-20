from daqc_plate import DaqcPlate
import sys
import time
import logger

class ADBoard(DaqcPlate):
    def __init__(self, pid, cfgObj):
        #try:
        self.name = "ADBoard_" + str(pid)
        self.pid = pid
        self.ll = logger.logger("ADBoard __int__ called")
            #self.alpha = cfgObj.alpha
        #except Exception ex:
        #    sys.exit("Error in " + "DaqcPlate")

    def get_adc(self, idx):
        return DaqcPlate.get_adc(self.pid, idx)
    #get_adc

    def get_temp(self, idx, scale='f'):
        return DaqcPlate.get_temp(self.pid, idx, scale)
        #return DaqcPlate.km(self) 

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
