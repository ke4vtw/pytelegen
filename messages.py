# Message Base Class
import jsonpickle
import datetime


class Message:

    def __init__(self, domain, action):
        self.domain = domain
        self.action = action

    def __str__(self):
        return jsonpickle.encode(self)

    def getResponse(self):
        tmp = jsonpickle.encode(self)
        resp = jsonpickle.decode(tmp)
        resp.timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        return resp
