from ast import Str
import sys
import os
from datetime import datetime

tags = ['add one url','remove one']
appLogs = []
epoch = datetime.utcfromtimestamp(0)


class DownloadAction:
    url = ""
    action_add = epoch
    action_remove = epoch

    def parse(self, l):
        if tags[0] in l:
            return self.addOne(l)
        elif tags[1] in l:
            return self.remove(l)
        else :
            return False

    def addOne(self, l):
        tag = tags[0]
        if len(self.url) > 0:
            return False
        self.url = self.stringBettwen(l, tag, ']')
        self.action_add = timeFromLine(l)
        return True
    
    def remove(self, l):
        tag = tags[1]
        b = 'url.'
        e = ' opt:'
        url = self.stringBettwen(l, b, e)
        if len(self.url) > 0:
            if self.url in url:
                if self.action_remove == epoch:
                    self.action_remove = timeFromLine(l)
                    return True
        return False

    def stringBettwen(self, l, b, e):
        i = l.find(b)
        if i < 0:
            return None
        i += len(b)

        j = len(l)
        if e != None:
            j = l.find(e, i)
        if j < 0:
            return None
        return l[i:j].strip('[').strip(']').strip()

class UrlRunTime:
    start = epoch
    complete = epoch
    traceId = ""
    urltext = ""
    succeed = False

class AppRun:
    appRunDate = epoch
    actionList = []

def timeDiff(dt1, dt2):
    return (dt1 - dt2).total_seconds()

def urlFromLine(l):
    for x in tags:
        if x in l:
            return x;
    return ''

def timeFromLine(lw):
    ls = lw.split()
    if len(ls) <= 2:
        return epoch
    
    ts = ls[0] + ' ' + ls[1]

    a = ts.split('.')
    if len(a) > 1:
        if len(a[1]) == 1:
            ts = a[0]+'.00'+a[1]
        elif len(a[1]) == 2:
            ts = a[0]+'.0'+a[1]

    if len(ts) > 24:
        return datetime.utcfromtimestamp(100000)

    t = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
    return t

def findUrl(id, list):
    for x in list:
        if x.traceId == id:
            return x
    return None

def actionDataFromLine(appRun, l):
    for action in appRun.actionList:
        if action.parse(l):
            return
    action = DownloadAction()
    if action.parse(l):
        appRun.actionList.append(action)
    else :
        print("lost:" + l)
    return

def appRunTimeFromLine(l):
    if 'app started' in l:
        return datetime.utcfromtimestamp(1)
    return epoch

def loadLog(path):
    print("loading " + path)
    file = open(path, 'r')
    lines = file.readlines()

    appRun = AppRun()
    for l in lines:
        t = appRunTimeFromLine(l)
        if t != epoch:
            run = AppRun()
            run.appRunDate = t
            appLogs.append(run)
            run.actionList = []
            appRun = run
        elif appRun.appRunDate != epoch:
            for x in tags:
                if x in l:
                    actionDataFromLine(appRun, l)
                    break



    print("app run times:" + str(len(appLogs)))
    resultPath = path + "_image.csv"
    
    f = open(resultPath, "w")
    f.write("apprun, Url,add,remove,Duration\n")
    index = 0
    for log in appLogs:
        index = index + 1
        print("download times:" + str(len(log.actionList)))
        for r in log.actionList:
            f.write(str(index)+"," + r.url + "," + str(r.action_add) + ","  + str(r.action_remove) +"," + str(timeDiff(r.action_remove, r.action_add)) + os.linesep ) 
    f.close()
    print("output: " + resultPath)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        loadLog(os.path.abspath(sys.argv[1]))
    else :
        print("python analysis.py logfile_path")