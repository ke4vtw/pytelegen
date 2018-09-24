import os
import platform

import psutil


class ProcInfo:
    procId = os.getpid()
    p = psutil.Process(procId)
    procName = p.name()
    procCmdLine = p.cmdline()
    procMachine = platform.uname()
    procUserName = p.username()
    procCurFolder = p.cwd()

    def stamp(self, msg):
        pInfo = type('', (), {})()
        pInfo.processId = ProcInfo.procId
        pInfo.processName = ProcInfo.procName
        pInfo.processCmdLine = ProcInfo.procCmdLine
        pInfo.machine = ProcInfo.procMachine[1]
        pInfo.username = ProcInfo.procUserName
        pInfo.currentFolder = ProcInfo.procCurFolder
        msg.processInfo = pInfo
        return msg
