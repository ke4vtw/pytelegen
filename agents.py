import os
import socket
import subprocess
from urlparse import urlparse

import procInfo


class FileAgent:

    homeFolder = os.path.expanduser("~")

    def handle(self, msg):
        dispatcher = {
            "Create": self.handleCreate,
            "Update": self.handleUpdate,
            "Delete": self.handleDelete
        }
        handler = dispatcher.get(msg.action, self.handleUnknown)
        return handler(msg)

    def handleCreate(self, msg):
        fn = msg.fileName.replace("~", FileAgent.homeFolder)
        f = open(fn, "w+")
        f.close()
        resp = msg.getResponse()
        resp.fileName = fn # update to full path
        return resp

    def handleUpdate(self, msg):
        fn = msg.fileName.replace("~", FileAgent.homeFolder)
        f = open(fn, "a+")
        if hasattr(msg, "append"):
            f.write(msg.append)
        if hasattr(msg, "appendline"):
            f.write(msg.appendline + "\n")
        f.close()
        resp = msg.getResponse()
        resp.fileName = fn  # update to full path
        return resp

    def handleDelete(self, msg):
        fn = msg.fileName.replace("~", FileAgent.homeFolder)
        os.remove(fn)
        resp = msg.getResponse()
        resp.fileName = fn  # update to full path
        return resp

    def handleUnknown(self, msg):
        return None


class ProcessAgent:

    def __init__(self):
        pass

    def handle(self, msg):
        resp = msg.getResponse()
        resp.spawnedpid = subprocess.Popen(msg.command).pid
        return resp


class NetworkAgent:

    CONNECTION_TIMEOUT = 5
    CHUNK_SIZE = 1024
    HTTP_VERSION = 1.0
    CRLF = "\r\n\r\n"

    def __init__(self):
        pass

    def handle(self, msg):
        s = socket.socket()
        url = urlparse(msg.url)

        resp = self._get(msg)
        resp.protocol = url.scheme
        if hasattr(url, "port"):
            vals = url.netloc.split(':')
            resp.baseurl = vals[0]
            resp.port = url.port or 80
        else:
            resp.baseurl = url.netloc
            resp.port = 80
        resp.path = url.path
        resp.params = url.params
        resp.query = url.query
        resp.fragment = url.fragment

        return resp

    def _receive_all(self, sock, chunk_size=CHUNK_SIZE):
        """Gather all the data from a request."""
        chunks = []
        while True:
            chunk = sock.recv(int(chunk_size))
            if chunk:
                chunks.append(chunk)
            else:
                break

        return ''.join(chunks)

    def _get(self, req, **kw):
        url = req.url
        kw.setdefault('timeout', self.CONNECTION_TIMEOUT)
        kw.setdefault('chunk_size', self.CHUNK_SIZE)
        kw.setdefault('http_version', self.HTTP_VERSION)
        url = urlparse(url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(kw.get('timeout'))
        sock.connect((url.netloc, url.port or 80))

        msg = 'GET {0} HTTP/{1} {2}'.format(url.path or '/', kw.get('http_version'), self.CRLF)

        resp = req.getResponse()
        sock.sendall(msg)
        resp.bytesSent = len(msg)

        self._receive_all(sock, chunk_size=kw.get('chunk_size'))
        sock.close()

        return resp


class Agent:
    agents = dict(File=FileAgent(), Process=ProcessAgent(), Network=NetworkAgent())

    def __init__(self):
        self.procInfo = procInfo.ProcInfo()

    def handle(self, msg):
        agent = Agent.agents[msg.domain]
        results = self.procInfo.stamp(agent.handle(msg))
        return results
