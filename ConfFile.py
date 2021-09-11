import json
import logger
from Request import Request

class ConfFile:
    def __init__(self, conf_dict, logger, e_quit):
        self.e_quit = e_quit
        self.ll = logger
        self.last_runtimes_updated_time = "lastupdatedatetime"
        self.counter = 21
        self.request = Request('http://192.168.1.106/', self.ll)

    def read_conf(cls, mode):
        conf_file = open("irrigation.conf", mode)
        conf_data = conf_file.read()
        conf_json = json.loads(conf_data)
        cls.ll.log("conf_json: " + str(conf_json))
        conf_file.close()

        return conf_json

    def write_conf(cls, conf_json):
        return 0        


    #TODO Have this return [ret_val, man_run], python array with 2 bools
    def check_for_update(cls, conf_file, run_times_mode):
        cls.counter += 1
        cls.ll.log("COUNTER: " + str(cls.counter))
        ret_val = False 
        man_run = None
        cls.ll.log("run_times_mode: " + str(run_times_mode))
        #run_times_mode[0] = run_times_mode[0] + 1
        if cls.counter > 20:
            cls.counter = 0
            try:
                rta = cls.request.http_get('temp/runtimesaudit/1')
                rta_json = json.loads(str(rta.text))
                cls.ll.log("rta_json['date_modified']: " + str(rta_json['date_modified']))
                cls.ll.log("cls.last_runtimes_updated_time: " + str(cls.last_runtimes_updated_time))
                date_modified = rta_json['date_modified']
                if date_modified != cls.last_runtimes_updated_time:
                    cls.ll.log("cls.last_runtimes_updated_time: " + str(cls.last_runtimes_updated_time))
                    cls.last_runtimes_updated_time = date_modified
                    run_times = cls.request.http_get('temp/runtimes')
                    rtt_json = json.loads(run_times.text)
                    cls.ll.log("rtt_json: " + str(rtt_json))
                    run_times = [
                            [0, rtt_json[0]['v1'], rtt_json[0]['v2'], rtt_json[0]['v3'], rtt_json[0]['v4'], rtt_json[0]['v5'], rtt_json[0]['v6'], rtt_json[0]['v7']],
                            [0, rtt_json[1]['v1'], rtt_json[1]['v2'], rtt_json[1]['v3'], rtt_json[1]['v4'], rtt_json[1]['v5'], rtt_json[1]['v6'], rtt_json[1]['v7']],
                            [0, rtt_json[2]['v1'], rtt_json[2]['v2'], rtt_json[2]['v3'], rtt_json[2]['v4'], rtt_json[2]['v5'], rtt_json[2]['v6'], rtt_json[2]['v7']],
                            [0, rtt_json[3]['v1'], rtt_json[3]['v2'], rtt_json[3]['v3'], rtt_json[3]['v4'], rtt_json[3]['v5'], rtt_json[3]['v6'], rtt_json[3]['v7']],
                            [0, rtt_json[4]['v1'], rtt_json[4]['v2'], rtt_json[4]['v3'], rtt_json[4]['v4'], rtt_json[4]['v5'], rtt_json[4]['v6'], rtt_json[4]['v7']],
                            [0, rtt_json[5]['v1'], rtt_json[5]['v2'], rtt_json[5]['v3'], rtt_json[5]['v4'], rtt_json[5]['v5'], rtt_json[5]['v6'], rtt_json[5]['v7']],
                            [0, rtt_json[6]['v1'], rtt_json[6]['v2'], rtt_json[6]['v3'], rtt_json[6]['v4'], rtt_json[6]['v5'], rtt_json[6]['v6'], rtt_json[6]['v7']],
                        ]
                    man_times = [0, rtt_json[7]['v1'], rtt_json[7]['v2'], rtt_json[7]['v3'], rtt_json[7]['v4'], rtt_json[7]['v5'], rtt_json[7]['v6'], rtt_json[7]['v7']]
                    man_mode = rtt_json[7]['run_manual']
                    cls.ll.log("run_times: " + str(run_times))
                    cls.ll.log("man_mode: " + str(man_mode))
                    conf_data = ''
                    with open('irrigation.conf', 'r') as fp:
                        conf_data = fp.read()

                    conf_json = json.loads(conf_data)
                    conf_json['run_times'] = run_times
                    cls.ll.log("conf_json-conf_json: " + str(conf_json))

                    with open('irrigation.conf', 'w') as fp:
                        json.dump(conf_json, fp)
 
                    ret_val = True
            except Exception as ex:
                cls.ll.log("Exception: " + str(ex), 'e')
        ret_val = ret_val
        return ret_val
