import procInfo


class FileAgent:

    def handle(self, msg):
        dispatcher = {
            "Create": self.handleCreate,
            "Update": self.handleUpdate,
            "Delete": self.handleDelete
        }
        handler = dispatcher.get(msg.action, self.handleUnknown)
        return handler(msg)

    def handleCreate(self, msg):
        print ("{0} {1} {2}".format(msg.domain, msg.action, msg.fileName))
        # fn = msg.fileName
        # f = open(fn, "w+")
        # f.close()
        resp = msg.getResponse()
        return resp

    def handleUpdate(self, msg):
        print ("{0} {1} {2}".format(msg.domain, msg.action, msg.fileName))
        # fn = msg.fileName
        # txt = msg.txt
        # f = open(fn, "a+")
        # f.write(txt)
        # f.close()
        resp = msg.getResponse()
        return resp

    def handleDelete(self, msg):
        print ("{0} {1} {2}".format(msg.domain, msg.action, msg.fileName))
        resp = msg.getResponse()
        return resp

    def handleUnknown(self, msg):
        return None


class ProcessAgent:

    def __init__(self):
        pass

    def handle(self, msg):
        print ("{0} {1} {2} {3}".format(msg.domain, msg.action, msg.executable, msg.parameters))
        resp = msg.getResponse()
        return resp


class NetworkAgent:

    def __init__(self):
        pass

    def handle(self, msg):
        print ("{0} {1} {2}".format(msg.domain, msg.action, msg.url))
        resp = msg.getResponse()
        return resp


class Agent:
    agents = dict(File=FileAgent(), Process=ProcessAgent(), Network=NetworkAgent())

    def __init__(self):
        self.procInfo = procInfo.ProcInfo()

    def handle(self, msg):
        agent = Agent.agents[msg.domain]
        results = self.procInfo.stamp(agent.handle(msg))
        return results
