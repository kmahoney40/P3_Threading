import requests
import json
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class Request():
    def __init__(self, url, loglog):
        self.name  = 'Request'
        self.ll = loglog
        self.url = url
        
    def http_get(cls, path):
        #return "TODO: implement http_get"
        try:
            if not (isinstance(path, str) and len(path)):
                raise ValueError('path: ' + str(path) + ' is not a string or is empty')

            #KMDB verify=False is a hack to get around the fact that the cert is self signed or not signed at all
            ret = requests.get(cls.url + path, verify=False)
            cls.ll.log('request url + path: ' + str(ret.text), 'd')
            return ret
        except ValueError as ex:
            cls.ll.log('Request.http_get argument exception: ' + str(ex), 'e')
            return str(ex)
        except Exception as ex:
            cls.ll.log('Request.http_get exception: url=' + cls.url + ', path=' + path + 'Exception:' + str(ex), 'e' )
        
    # def http_post(cls, path, headers, data):
    #     ret = requests.post(cls.url + path, headers=headers, data=data)
    #     return ret
    #     #TODO add param checking and except Exception catch all error with logging. See http_get above
        
    def http_post(cls, path, data, headers):
        try:
            cls.ll.log('Request.http_post: url=' + cls.url + ', path=' + path + ', data= ' + str(data) + ', headers=' + str(data), 'd' )
            if not (isinstance(path, str) and len(path)):
                raise ValueError('path: ' + str(path) + ' is not a string or is empty')
            if not (len(str(data))):
                raise ValueError('data: ' + str(data) + ' is empty')
            if not (len(str(headers))):
                raise ValueError('headers: ' + str(headers) + ' is empty')
            
            data_json = json.dumps(data)
            
            urllib3.disable_warnings(InsecureRequestWarning)
            
            # timeout=5 call will return after 5 seconds if no response
            ret = requests.post(cls.url + path, data=data_json, headers=headers, verify=False, timeout=5)
            
            # Also consider using eventlet to timeout the request
            # import requests
            # import eventlet
            #     eventlet.monkey_patch()

            # with eventlet.Timeout(10):
            #     requests.get("http://ipv4.download.thinkbroadband.com/1GB.zip", verify=False)
            
            cls.ll.log("Request.http_post: ret=[" + str(ret) + "]", "d")
        except ValueError as ex:
            cls.ll.log('Request.http_post argument exception: ' + str(ex), 'e')
            ret = str(ex)
        except Exception as ex:
            cls.ll.log('Request.http_post exception: url=' + cls.url + ', path=' + path + ', data= ' + str(data) + ', headers=' + str(data) + ' Exception:' + str(ex), 'e' )
            ret = str(ex)

        return ret
        
        
    def http_put(cls, path, data, headers):
        try:
            if not (isinstance(path, str) and len(path)):
                raise ValueError('path: ' + str(path) + ' is not a string or is empty')
            if not (len(str(data))):
                raise ValueError('data: ' + str(data) + ' is empty')
            if not (len(str(headers))):
                raise ValueError('headers: ' + str(headers) + ' is empty')
            
            ret = requests.put(cls.url + path, data = data, headers=headers)
        except ValueError as ex:
            cls.ll.log('Request.http_put argument exception: ' + str(ex), 'e')
            ret = str(ex)
        except Exception as ex:
            cls.ll.log('Request.http_put exception: url=' + cls.url + ', path=' + path + ', data= ' + str(data) + ', headers=' + str(data) + ' Exception:' + str(ex), 'e' )
            ret = str(ex)

        return ret
    