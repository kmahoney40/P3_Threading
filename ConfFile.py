import json
import logger

class ConfFile:
    def __init__(self, conf_dict):
        #self.conf_file
        #open("irrigation.conf", "r")
        #self.conf_dict = conf_dict
        self.ll = logger

        #conf_data = self.conf_file.read()
        #conf_json = json.loads(conf_data)
        #self.ll.log("TEST DICT: woot!!!!!!!!!!!: " + str(conf_dict), 'd')

    def read_conf(cls):
        conf_file = open("irrigation.conf", "r")
        conf_data = conf_file.read()
        conf_json = json.loads(conf_data)

        return conf_json

    def write_conf(cls, conf_json):
        
