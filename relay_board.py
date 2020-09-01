from relay_plate import RelayPlate
import sys
import time
import logger

class RelayBoard(RelayPlate):
    def __init__(self, pid, configObj):
        self.name = "RelayBoard_" + str(pid)
        self.pid = pid
        self.o = configObj
        self.ll = logger.logger("ADBoard __int__ called")
    # __init__

    def  set_relay(cls, rid, state):
        RelayPlate.set_relay(rid, state)

    def relay_off(cls, rid):
        RelayPlate.relay_off(rid, rid)

    def relay_toggle(cls, rid):
        RelayPlate.relay_toggle(0, rid)
        cls.ll.log("relay_toggle: " + str(rid))

    def set_led(cls):
        RelayPlate.set_led(self.pid)

    def clr_led(cls):
        RelayPlate.clr_led(self.pid)
