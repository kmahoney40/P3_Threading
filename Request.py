import requests

class Request():
    def __init__(self, url, loglog):
        self.name  = 'Request'
        self.ll = loglog
        self.url = url
        
    def http_get(cls, path):
        try:
            if not (isinstance(path, str) and len(path)):
                raise ValueError('path: ' + str(path) + ' is not a string or is empty')

            ret = requests.get(cls.url + path)
            cls.ll.log('request url + path: ' + str(ret.text), 'd')
            return ret
        except ValueError as ex:
            cls.ll.log('Request.http_get argument exception: ' + str(ex), 'e')
            return str(ex)
        except Exception as ex:
            cls.ll.log('Request.http_get exception: url=' + cls.url + ', path=' + path + 'Exception:' + str(ex), 'e' )
        
    def http_post(cls, path, headers, data):
        ret = requests.post('http://192.168.1.106/temp/', headers=headers, data=data)
        return ret
        #TODO add param checking and except Exception catch all error with logging. See http_get above
        