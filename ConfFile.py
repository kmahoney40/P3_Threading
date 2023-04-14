import json
from sys import exc_info
import logger
from Request import Request

class ConfFile:
    def __init__(self, in_dict, logger, is_man_run, e_quit):
        self.is_man_run = is_man_run
        self.e_quit = e_quit
        self.in_dict = in_dict
        self.ll = logger
        self.last_runtimes_updated_time = "lastupdatedatetime"
        self.counter = 14
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


    def check_for_update(cls, run_times_mode, mode, water_dict):
        cls.counter += 1
        cls.ll.log("COUNTER: " + str(cls.counter))
        ret_val = False 
        cls.ll.log("run_times_mode: " + str(run_times_mode))

        if cls.counter > 5:
            cls.counter = 0
            cls.ll.log("==========  13  ==============", "d")
            try:
                rta = cls.request.http_get('api/runtimesaudit/1')
                rta_json = json.loads(str(rta.text))
                cls.ll.log("rta_json['date_modified']: " + str(rta_json['date_modified']))
                cls.ll.log("cls.last_runtimes_updated_time: " + str(cls.last_runtimes_updated_time))
                date_modified = rta_json['date_modified']
                if date_modified != cls.last_runtimes_updated_time:
                    cls.ll.log("==========  DIFF  ==============", "d")
                    cls.ll.log("cls.last_runtimes_updated_time: " + str(cls.last_runtimes_updated_time))
                    cls.last_runtimes_updated_time = date_modified
                    run_times = cls.request.http_get('api/runtimes')
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
                            [0, rtt_json[7]['v1'], rtt_json[7]['v2'], rtt_json[7]['v3'], rtt_json[7]['v4'], rtt_json[7]['v5'], rtt_json[7]['v6'], rtt_json[7]['v7']]
                        ]
                    
                    if rtt_json[7]['run_manual'] == 1:
                        cls.in_dict["man_mode"] = 1
                        cls.is_man_run[0] = True
                        newHeaders = {'Content-type': 'application/json'}
                        my_json_string = json.dumps({"run_manual":0})

                        try:
                            ret = cls.request.http_put('api/runtimes/8/', data=my_json_string, headers=newHeaders)
                            cls.ll.log("http_post api/runtimes/8/: " + str(ret.json))
                        except:
                            cls.ll.log("Error in http_post call if ConfFile.py: " + str(exc_info()[0]), "e")

                    cls.ll.log("$$ ConfFile.check_for_update: run_times: " + str(run_times))
                    
                    water_dict['conf']['run_times'] = run_times
                    cls.ll.log("*** str(water_dict[conf][run_times] " + str(water_dict['conf']['run_times']))

                    conf_data = ''
                    with open('irrigation.conf', 'r') as fp:
                        conf_data = fp.read()

                    conf_json = json.loads(conf_data)
                    conf_json['run_times'] = run_times
                    cls.ll.log("############conf_json-conf_json: " + str(conf_json))
                    cls.ll.log("############conf_json-conf_json: " + str(conf_json))
                    cls.ll.log("############conf_json-conf_json: " + str(conf_json))
                    cls.ll.log("############conf_json-conf_json: " + str(conf_json))

                    with open('irrigation.conf', 'w') as fp:
                        json.dump(conf_json, fp)

                    ret_val = True
            except Exception as ex:
                cls.ll.log("Exception: " + str(ex), 'e')

        return ret_val
