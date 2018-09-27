import datetime
import sys
import json
import jsonpickle
import os
import platform
import psutil
import socket
import subprocess
from urlparse import urlparse

class Message:

    procId = os.getpid()
    p = psutil.Process(procId)

    pInfo = type('', (), {})()
    pInfo.processId = procId
    pInfo.processName = p.name()
    pInfo.processCmdLine = p.cmdline()
    pInfo.machine = platform.uname()[1]
    pInfo.username = p.username()
    pInfo.currentFolder = p.cwd()

    def __init__(self, domain, action):
        self.domain = domain
        self.action = action

    def __str__(self):
        return jsonpickle.encode(self)

def get_response(msg):
    resp = jsonpickle.decode(jsonpickle.encode(msg))
    resp.timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
    resp.processInfo = Message.pInfo
    return resp

def network_get(msg):
    url = urlparse(msg.url)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((url.netloc, url.port or 80))

    http = 'GET {0} HTTP/{1} {2}'.format(url.path or '/', 1.0, "\r\n\r\n")

    resp = get_response(msg)
    sock.sendall(http)
    resp.bytesSent = len(http)
    sock.close()

    resp.protocol = url.scheme
    if hasattr(url, "port"):
        resp.baseurl = url.netloc.split(':')[0]
        resp.port = url.port or 80
    else:
        resp.baseurl = url.netloc
        resp.port = 80
    resp.path = url.path
    resp.params = url.params
    resp.query = url.query
    resp.fragment = url.fragment

    return resp

def process_spawn(msg):
    resp = get_response(msg)
    resp.spawnedpid = subprocess.Popen(msg.command).pid
    return resp

def file_update(msg):
    fn = msg.fileName.replace("~", homeFolder)
    if msg.action == "Delete":
        os.remove(fn)
    else:
        f = open(fn, "a+")
        if hasattr(msg, "append"):
            f.write(msg.append)
        if hasattr(msg, "appendline"):
            f.write(msg.appendline + "\n")
        f.close()  # just create the file!
    resp = get_response(msg)
    resp.fileName = fn  # update to full path
    return resp

handlers = dict(
    FileCreate=file_update,
    FileUpdate=file_update,
    FileDelete=file_update,
    NetworkGet=network_get,
    ProcessSpawn=process_spawn
)
homeFolder = os.path.expanduser("~")
ops = jsonpickle.decode("\n".join(sys.stdin.readlines()))
results = []
for op in ops:
    results.append(handlers[op.domain+op.action](op))
print json.dumps(results, default=lambda o: o.__dict__, indent=4)
