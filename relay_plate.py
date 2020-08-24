import piplates.RELAYplate as RELAY
import sys
import time
import logger

class RelayPlate:
    def __init__(self, pid, cfg_obj):
        try:
            self.pid = pid
        except:
            sys.exit("Error in RelayPlate: " + sys.exc_info()[0])
    # __init__

    def set_relay(cls, rid, state):
        if state != 0:
            RELAY.realyON(cls.pid, rid)
        else:
            RELAY.relayOFF(cls.pid, rid)
    # set_relay

    def relay_on(cls, rid):
        RELAY.relayON(0, rid)
    # relay_on

    def relay_off(cls, rid):
        RELAY.relayOFF(0, rid)
    # relay_off

    def relay_toggle(cls, rid):
        RELAY.relayTOGGLE(0, rid)
    # relay_toggle

    # Set all the relays in 1 command. val is a 7 bit number
    # each bit corresponding to a relay. 100 1110 will set relays
    # 2, 3, 4, 7 and clear the others
    def relay_all(cls, val):
        RELAY.relayALL(cls.pid, val)
    # relay_all

    # returns a 7 bit number as the state of all relays on a board
    def relay_state(cls, addr):
        RELAY.relaySTATE(addr)
    # relay_state

    # Turn led on
    def set_led(cls, addr):
        RELAY.setLED(addr)
    # set_led

    # Turn led off
    def clr_led(cls, addr):
        RELAY.clrLED(addr)
    # clr_led

    def toggle_led(cls, addr):
        RELAY.toggleLED(addr)
    # toggle_led