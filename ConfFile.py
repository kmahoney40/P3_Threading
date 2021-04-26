import json
import logger
from Request import Request

class ConfFile:
    def __init__(self, conf_dict, logger):
        #self.conf_file
        #open("irrigation.conf", "r")
        #self.conf_dict = conf_dict
        self.ll = logger
        self.last_runtimes_updated_time = "lastupdatedatetime"
        self.counter = 0
        self.request = Request('http://192.168.1.106/', self.ll)


        #conf_data = self.conf_file.read()
        #conf_json = json.loads(conf_data)
        #self.ll.log("TEST DICT: woot!!!!!!!!!!!: " + str(conf_dict), 'd')

    def read_conf(cls, mode):
        conf_file = open("irrigation.conf", mode)
        conf_data = conf_file.read()
        conf_json = json.loads(conf_data)
        cls.ll.log("conf_json: " + str(conf_json))
        conf_file.close()

        return conf_json

    def write_conf(cls, conf_json):
        return 0        

    def check_for_update(cls):
        cls.counter += 1
        cls.ll.log("COUNTER: " + str(cls.counter))
        ret_val = False

        if cls.counter > 55:
            cls.counter = 0
            try:
                rta = cls.request.http_get('temp/runtimesaudit/1')
                rta_json = json.loads(str(rta.text))
                date_modified =rta_json['date_modified']
                if date_modified != cls.last_runtimes_updated_time:
                    cls.last_runtimes_updated_time = date_modified
                    run_times = cls.request.http_get('temp/runtimes')
                    cls.ll.log("run_times: " + run_times.text)
                    rtt_json = json.loads(run_times.text)
                    cls.ll.log("rtt_json: " + str(rtt_json))
                    run_times1 = [
                            [0, rtt_json[0]['v1'], rtt_json[0]['v2'], rtt_json[0]['v3'], rtt_json[0]['v4'], rtt_json[0]['v5'], rtt_json[0]['v6'], rtt_json[0]['v7']],
                            [0, rtt_json[1]['v1'], rtt_json[1]['v2'], rtt_json[1]['v3'], rtt_json[1]['v4'], rtt_json[1]['v5'], rtt_json[1]['v6'], rtt_json[1]['v7']],
                            [0, rtt_json[2]['v1'], rtt_json[2]['v2'], rtt_json[2]['v3'], rtt_json[2]['v4'], rtt_json[2]['v5'], rtt_json[2]['v6'], rtt_json[2]['v7']],
                            [0, rtt_json[3]['v1'], rtt_json[3]['v2'], rtt_json[3]['v3'], rtt_json[3]['v4'], rtt_json[3]['v5'], rtt_json[3]['v6'], rtt_json[3]['v7']],
                            [0, rtt_json[4]['v1'], rtt_json[4]['v2'], rtt_json[4]['v3'], rtt_json[4]['v4'], rtt_json[4]['v5'], rtt_json[4]['v6'], rtt_json[4]['v7']],
                            [0, rtt_json[5]['v1'], rtt_json[5]['v2'], rtt_json[5]['v3'], rtt_json[5]['v4'], rtt_json[5]['v5'], rtt_json[5]['v6'], rtt_json[5]['v7']],
                            [0, rtt_json[6]['v1'], rtt_json[6]['v2'], rtt_json[6]['v3'], rtt_json[6]['v4'], rtt_json[6]['v5'], rtt_json[6]['v6'], rtt_json[6]['v7']]#,
                            #[0, rtt_json[7]['v1'], rtt_json[7]['v2'], rtt_json[7]['v3'], rtt_json[7]['v4'], rtt_json[7]['v5'], rtt_json[7]['v6'], rtt_json[7]['v7']]
                        ]

                    cls.ll.log("run_times1: " + str(run_times1))

                    #conf_file = cls.read_conf('r')

                    conf_file = open("irrigation.conf", 'r')
                    conf_data = conf_file.read()
                    conf_json = json.loads(conf_data)
                    conf_file.close()

                    conf_file = open("irrigation.conf", 'w')
                    conf_file.write(json.dumps(conf_json))
                    conf_file.close()


                    cls.ll.log("run_times1: " + str(run_times1))
                    cls.write_conf(run_times)
                    cls.read_conf('r')
                    ret_val = True
            except Exception as ex:
                cls.ll.log("Exception: " + str(ex), 'e')

        return ret_val
