#from relay_plate import RelayPlate
import piplates.RELAYplate as RELAY
import sys
import time
import logger

#todo oConf is water_dict in main, rename.
class RelayBoard:
    def __init__(self, pid, logger, oConf):
        self.name = "RelayBoard_" + str(pid)
        self.pid = pid
        self.oConf = oConf
        self.ll = logger# logger.logger("ADBoard __int__ called")
        self.ll.log("RelayBoard __int__ pid = " + str(self.pid))
        self.ll.log("RelayBoard oConf = " + str(self.oConf))
        #self.Relay_Plate = RelayPlate(self.pid, self.o)
        #super().__init__(self.pid, self.o)
    # __init__

    def set_relay(cls, rid, state):
        if state != 0:
            RELAY.realyON(cls.pid, rid)
        else:
            RELAY.relayOFF(cls.pid, rid)
    # set_relay

    def relay_on(cls, rid):
        cls.ll.log("relay_plate BEFORE relay_on")
        RELAY.relayON(cls.pid, rid)
        cls.ll.log("relay_plate AFTER relay_on")

    def relay_off(cls, rid):
        cls.ll.log("2-relay_plate BEFORE relay_off")
        RELAY.relayOFF(cls.pid, rid)
        cls.ll.log("2-relay_plate AFTER relay_off")

    def relay_toggle(cls, rid):
        cls.ll.log("relay_toggle: " + str(rid))
        RELAY.relayTOGGLE(cls.pid, rid)

    def set_all_relays(cls, val):
        RELAY.relayALL(cls.pid, val)

    def led_on(cls):
        cls.ll.log("led_on: WOOT")
        RELAY.setLED(cls.pid)

    def led_off(cls):
        try:
            cls.ll.log("led_off pid: " + str(cls.pid))
            RELAY.clrLED(cls.pid)
        except:
            sys.exit("Error in RelayBoard: " + str(sys.exc_info()[0]))

    def led_toggle(cls):
        RELAY.toggleLED(cls.pid)
        
    def get_relay_state(cls):
        return RELAY.relaySTATE(cls.pid)
